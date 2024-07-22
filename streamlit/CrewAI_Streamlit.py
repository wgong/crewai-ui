# To install required packages:
# pip install crewai==0.22.5 streamlit==1.32.2
from pathlib import Path

import streamlit as st

from crewai import Crew, Process, Agent, Task
from langchain_core.callbacks import BaseCallbackHandler
from typing import TYPE_CHECKING, Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import Tool
# from crewai_tools import (
#     SerperDevTool, ScrapeWebsiteTool, 
# #     WebsiteSearchTool, MDXSearchTool,
# #     DirectoryReadTool, FileReadTool, BaseTool
# )
from langchain_community.utilities import GoogleSerperAPIWrapper

# from langchain.agents import load_tools

from dotenv import load_dotenv
import os
load_dotenv()

def create_folder(folder_path):
    try:
        p = Path(folder_path)
        # Create the folder, ignoring errors if it already exists
        p.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(str(e))

class MyCustomHandler(BaseCallbackHandler):
   
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        st.session_state.messages.append({"role": "assistant", "content": inputs['input']})
        st.chat_message("assistant").write(inputs['input'])
   
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        st.session_state.messages.append({"role": self.agent_name, "content": outputs['output']})
        st.chat_message(self.agent_name, avatar=avators[self.agent_name]).write(outputs['output'])


#==================
## Initialization
#==================
st.title("💬 CrewAI Writing Studio") 
avators = {
    "Writer":"https://cdn-icons-png.flaticon.com/512/320/320336.png",
    "Reviewer":"https://cdn-icons-png.freepik.com/512/9408/9408201.png"
}

file_suffix = "t6" 
folder_name = "outputs"
create_folder(folder_name)
fileout_write = Path(folder_name) / f"task_write-{file_suffix}.md"
fileout_review = Path(folder_name) / f"task_review-{file_suffix}.md"

if "messages" not in st.session_state:
    st.session_state["messages"] = [
            {
                "role": "assistant", 
                "content": "What blog post do you want us to write?"
            },
        ]

@st.cache_resource
def crewai_init(max_iter=10, max_rpm=10):
    
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL_NAME"),
    }
    # print(config)

    llm = ChatOpenAI(**config)

    serper_api_key=os.getenv("SERPER_API_KEY")
    # print(f"serper_api_key = {serper_api_key}")
    search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)

    # # Create and assign the search tool to an agent
    serper_tool = Tool(
        name="Intermediate Answer",
        func=search.run,
        description="Useful for search-based queries",
    )

    # tools = load_tools(["google-serper"])

    agent_write = Agent(
        role='Blog Post Writer',
        goal="Write and iterate a decent blog post.",
        backstory='''
                You are a blog post writer who is capable of writing a travel blog.
                You generate one iteration of an article once at a time.
                You never provide review comments.
                You are open to reviewer's comments and willing to iterate its article based on these comments.
            ''',
        tools=[serper_tool],  # This can be optionally specified; defaults to an empty list
        llm=llm,
        callbacks=[MyCustomHandler("Writer")],
        max_iter=max_iter,  # Optional
        max_rpm=max_rpm, # Optional
    )

    agent_review = Agent(
        role='Blog Post Reviewer',
        goal="list builtins about what need to be improved of a specific blog post. Do not give comments on a summary or abstract of an article",
        backstory='''
                You are a professional article reviewer and very helpful for improving articles.
                You review articles and give change recommendations to make the article more aligned with user requests.
                You will give review comments upon reading entire article, so you will not generate anything when the article is not completely delivered. 
                You never generate blogs by itself.
            ''',
        # tools=[serper_tool],  # This can be optionally specified; defaults to an empty list
        llm=llm,
        callbacks=[MyCustomHandler("Reviewer")],
        max_iter=max_iter,  # Optional
        max_rpm=max_rpm, # Optional
    )

    return llm, agent_write, agent_review

def main():
    llm, agent_write, agent_review = crewai_init()

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        task_write = Task(
            description=f"""Write a blog post of {prompt}. """,
            agent=agent_write,
            expected_output="an article under 300 words.",
            output_file=str(fileout_write),
        )

        task_review = Task(
            description="""list review comments for improvement from the entire content of blog post to make it more viral on social media""",
            agent=agent_review,
            expected_output="Builtin points about where need to be improved.",
            output_file=str(fileout_review),
        )

        # Establishing the crew with a hierarchical process
        project_crew = Crew(
            tasks=[task_write, task_review,],  # Tasks to be delegated and executed under the manager's supervision
            agents=[agent_write, agent_review,],
            manager_llm=llm,
            process=Process.hierarchical  # Specifies the hierarchical management approach
        )
        final = project_crew.kickoff()

        result = f"## Here is the Final Result \n\n {final}"
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.chat_message("assistant").write(result)

if __name__ == "__main__":
    main()