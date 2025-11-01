import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")


class CSVChat:
    def __init__(self, csv_files, openai_api_key, model="gpt-5-mini-2025-08-07"):
        """
        csv_files: dict like {'agriculture': 'crops.csv', 'climate': 'rainfall.csv'}
        openai_api_key: Your OpenAI API key
        model: OpenAI model (gpt-5-mini-2025-08-07, gpt-4o-mini, etc.)
        """
        self.llm = ChatOpenAI(
            api_key = openai_api_key,
            model_name=model,   
            temperature=1
        )
        self.data = {}

        # Load CSVs
        for name, path in csv_files.items():
            self.data[name] = pd.read_csv(path)
            print(f"✓ Loaded {name}: {self.data[name].shape[0]} rows, {self.data[name].shape[1]} columns")

    def chat(self, question):
        """Ask questions about your data"""

        # Prepare data context
        data_context = self._prepare_context()

        # Create prompt template
        template = """You are a data analyst expert. You have access to these datasets:

              {data_context}

              Available dataframe variables: {dataframes}

              User Question: {question}

              Your task:
              1. Analyze what data operations are needed
              2. Write Python pandas quick code to answer the question
              3. Store the final answer in a variable called 'answer'
              4. Make answer detailed and informative
              5. Return ONLY the Python code, no explanations
              6. Use the most efficient code to answer the question dont give any extra code or comments.


              Important:
              - Lower case all the str in dataset
              - Use proper pandas operations (groupby, merge, pivot, etc.)
              - Handle missing data appropriately
              - Format numbers nicely in the answer string
              - If comparing multiple things, present them clearly

              Example output:
              ```python
              # Calculate and compare averages
              mh_avg = climate[climate['State'] == 'Maharashtra']['Rainfall'].mean()
              ka_avg = climate[climate['State'] == 'Karnataka']['Rainfall'].mean()
              answer = f"Maharashtra: {{mh_avg:.2f}}mm\\nKarnataka: {{ka_avg:.2f}}mm"
              ```

              Now write code to answer the user's question:"""

        prompt = PromptTemplate(
            input_variables=["data_context", "dataframes", "question"],
            template=template
        )

        # Create chain
        chain = LLMChain(llm=self.llm, prompt=prompt)

        # Get response
        response = chain.run(
            data_context=data_context,
            dataframes=', '.join(self.data.keys()),
            question=question
        )

        # Extract code
        code = self._extract_code(response)

        # Execute and get answer
        result = self._execute_code(code)

        return {
            'answer': result,
            'code': code,
            'raw_response': response,
            'data_context': data_context
        }

    def _prepare_context(self):
        """Create summary of datasets"""
        context = ""

        for name, df in self.data.items():
            context += f"\n{'='*50}\n"
            context += f"Dataset: {name}\n"
            context += f"{'='*50}\n"
            context += f"Rows: {df.shape[0]} | Columns: {df.shape[1]}\n\n"
            context += f"Columns and types:\n"

            for col, dtype in df.dtypes.items():
                context += f"  - {col} ({dtype})"
                if dtype == 'object':
                    context += f" [{df[col].nunique()} unique values]"
                context += "\n"

            context += f"\nSample data (first 3 rows):\n"
            context += df.head(3).to_string(index=False) + "\n"

        return context

    def _extract_code(self, response):
        """Extract Python code from LLM response"""
        code = response.strip()

        # Remove markdown code blocks
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]

        return code.strip()

    def _execute_code(self, code):
        """Execute generated pandas code"""
        try:
            # Create execution namespace
            namespace = {
                'pd': pd,
                **self.data  # Add all dataframes
            }

            # Execute code
            exec(code, namespace)

            # Get answer
            if 'answer' in namespace:
                return namespace['answer']
            else:
                return "✓ Code executed successfully, but no 'answer' variable found"

        except Exception as e:
            error_msg = f"❌ Execution Error: {str(e)}\n\n"
            error_msg += f"Generated code:\n{'-'*50}\n{code}\n{'-'*50}"
            return error_msg


