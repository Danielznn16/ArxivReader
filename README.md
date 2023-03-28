# ArxivReader
This repository recieves Arxiv's daily update for its publishment, and converts it to be readable in a reader.

To run the parser, first deploy a MongoDB, then run 

```bash
python3 run.py
```

To activate the frontend,

```bash
streamlit run frontend.py
```

To turn on the mark read/good ability, input the right username, the default username is `owner`
