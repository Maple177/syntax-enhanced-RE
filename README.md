# Syntax-Enhanced Relation Extraction

***Syntax-enhanced RE models with depedency / constituency analysis***

:star: This codebase provides scripts of applying syntax-enhanced models on biomedical RE datasets as described in the paper:
https://academic.oup.com/database/article/doi/10.1093/database/baac070/6675625. 

This is an improved version including replacing BioBERT with PubMedBERT and other details.

There are four models either dependency-syntax-enhanced or constituency-syntax-enhanced:
- CE-PubMedBERT (constituency)
- CT-PubMedBERT (constituency)
- Late-fusion (dependency)
- MTS-PubMedBERT (dependency)

:star: Pre-processing scripts are provided under the directory /preprocessing/. Note that we use PubMedBERT tokenizer for wordpiece-level tokenization before pre-processing (change PubMedBERT to other BERT variants on your need):
```
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
```
Refer to the README file in the preprocessing folder for subsequent steps (if you want to use your own corpus).

🔨 You can skip pre-processing and download data for syntax-enhanced models (BB-Rel, ChemProt, DrugProt) here:

You can also generate these data using our pre-processing scripts (Refer to /preprocessing/).
