.PHONY: demo clean

demo:
	python3 examples/python_quickstart.py
	python3 examples/mcp_quickstart.py
	python3 examples/langgraph_quickstart.py
	python3 examples/openai_agents_quickstart.py

clean:
	rm -rf archives __pycache__ jep_quickstart/__pycache__ examples/__pycache__
