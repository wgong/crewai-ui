## CrewAI_Streamlit by yeyu_lab

### Setup

```
$ cd ~/projects/wgong/crewai-ui
$ streamlit run streamlit/CrewAI_Streamlit.py

```


## exa-crewai


## arXiv tool
crewai uses arxiv tool for research


### Setup
```
cd ~/projects/1_Biz/zilab
$ crewai create arxiv
$ cd arxiv
$ pip install poetry
$ poetry lock
$ poetry install

```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/arxiv/config/agents.yaml` to define your agents
- Modify `src/arxiv/config/tasks.yaml` to define your tasks
- Modify `src/arxiv/crew.py` to add your own logic, tools and specific args
- Modify `src/arxiv/main.py` to add custom inputs for your agents and tasks

### Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
poetry run arxiv
```

This command initializes the arxiv Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

### Understanding Your Crew

The arxiv Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.


### Resources

- https://github.com/wgong/exa-crewai  in ~/projects/1_Biz/zilab

- https://github.com/gongwork/arxiv-chainlit in ~/projects/gongwork
