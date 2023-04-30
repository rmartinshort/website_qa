import openai
import datetime
from openai.embeddings_utils import distances_from_embeddings

# needs langchain 0.0.153 +
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import PromptTemplate


class Chatter:
    def __init__(
        self,
        embeddings_df,
        embeddings_model="text-embedding-ada-002",
        response_model="gpt-3.5-turbo",
        use_langchain=True,
        verbose=True,
    ):
        self.embeddings = embeddings_df
        self.embeddings_model = embeddings_model
        self.response_model = response_model

        for col in self.embeddings.columns:
            if "embedding" in col:
                self.embeddings_col = col
                break
        self.text_col = "text"
        self.ntokens_col = "n_tokens"

        assert self.text_col in self.embeddings.columns
        assert self.ntokens_col in self.embeddings.columns

        self.use_langchain = use_langchain
        if use_langchain:
            self.LLM, self.PROMPT = self.setup_model()
            self.CHAIN = LLMChain(llm=self.LLM, verbose=verbose, prompt=self.PROMPT)
            self.inc = 1
            self.history = {}
        else:
            self.LLM = None
            self.PROMPT = None
            self.CHAIN = None
            # only used with langchain
            self.history = {}

    def setup_model(self, max_tokens=200, stop_sequence=None, temperature=0):
        """
        Setup the langchain model
        """

        LLM = ChatOpenAI(
            model_name=self.response_model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
        )

        # the prompt template
        prompt_template = self.build_prompt_template_langchain()

        return LLM, prompt_template

    def create_context(self, question, max_len=1500):
        """
        Create a context for a question by finding the most similar context from the dataframe
        """

        # Get the embeddings for the question
        q_embeddings = openai.Embedding.create(
            input=question, engine=self.embeddings_model
        )["data"][0]["embedding"]

        # Get the distances from the embeddings
        # overwrites the distances column in the embeddings df, not great practice but OK for POC
        self.embeddings["distances"] = distances_from_embeddings(
            q_embeddings,
            self.embeddings[self.embeddings_col].values,
            distance_metric="cosine",
        )

        returns = []
        cur_len = 0

        # Sort by distance and add the text to the context until the context is too long
        for i, row in self.embeddings.sort_values("distances", ascending=True).iterrows():
            # Add the length of the text to the current length
            cur_len += row[self.ntokens_col] + 4

            # If the context is too long, break
            if cur_len > max_len:
                break

            # Else add it to the text that is being returned
            returns.append(row[self.text_col])

        # Return the context
        return "\n\n###\n\n".join(returns)

    def interactive(self):
        """
        Interact with the chatbot via a command line interface
        :return:
        """

        # really simple method of interacting with the chat
        end_session = False
        while not end_session:
            user_input = input("Enter a question (Q to quit):")
            if user_input == "Q":
                end_session = True

            else:
                print("-" * 20)
                print("You asked \n {} \n".format(user_input))
                res = self.answer_question(user_input, debug=False)
                print(res)

    def answer_question(self, question, debug=True, max_len_context=2000):
        """
        Answer a question
        """

        # collect the context using embedding search
        context = self.create_context(question, max_len=max_len_context)

        if self.use_langchain:
            # if using langchain, just call the langchain
            result = self.CHAIN.predict_and_parse(context=context, question=question)

            # record chat history
            self.history[self.inc] = {
                "time": datetime.datetime.strftime(
                    datetime.datetime.now(), format="%Y-%m-%d %H:%M:%S'"
                ),
                "question": question,
                "context": context,
                "answer": result,
            }
            self.inc += 1

        else:
            # if not, call the API directly
            messages = self.build_prompt(question, context)

            if debug:
                print("prompt:\n" + str(messages))
                print("\n\n")

            try:
                # Create a completions using the question and context
                response = openai.ChatCompletion.create(
                    messages=messages,
                    temperature=0,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    model=self.response_model,
                )
                result = response["choices"][0].message["content"]
            except Exception as e:
                print(e)
                result = ""

        return result

    @staticmethod
    def build_prompt(question, context):
        """
        Make a prompt on the fly (when not using langchain)
        :param question:
        :param context:
        :return:
        """

        prompt = f"""
        Use the context delimited by triple backticks to answer the question below \
        If the question can't be answered based on the context but you can form an \
        answer from your own knowledge, answer as best you can but also say \
        "This answer is only partially based on the context provided". \
        If you can't answer the question, just say "I don't have enough information". \
        Output a JSON object with "answer" as a key and your answer as the corresponding value


        Question: {question}
        Context: ```{context}```
        Output JSON:
        """

        system_role = f"""
        You are a helpful assistant that answers questions based on relevant context
        """

        messages = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt},
        ]

        return messages

    @staticmethod
    def build_prompt_template_langchain():
        """
        Make a prompt template
        :return:
        """

        prompt_template = """
        Use the context delimited by triple backticks to answer the question below \
        If the question can't be answered based on the context but you can form an \
        answer from your own knowledge, answer as best you can but also say \
        "This answer is only partially based on the context provided". \
        If you can't answer the question, say "I don't have enough information". \
        Output a JSON object with "answer" as a key and your answer as the corresponding value

        Question: {question}
        Context: ```{context}```
        Output JSON
        """

        langchain_template = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        return langchain_template
