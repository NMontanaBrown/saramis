# Running RL Experiments

## Installation

As outlined in `/docs/install/SARAMIS.md`, create an enviroment for navigation.

```bash
conda env create -n saramis_rl_env_nav --f saramis_rl_env_nav.yml
conda activate saramis_rl_env_nav
```

## Training

From the activated environment, change the paths to /rl_expt folder provided, where the colon.xml file is at `./saramis/nav_rl/colon.xml`, and save_path points to a folder to save models during training. Then, run the following command:

```bash
python ./saramis/nav_rl/train.py
```

## Eval - Target Navigation

We provide a script to evaluate the trained agent on unseen test data.

```bash
python ./saramis/nav_rl/eval/eval.py
```


## Eval - Human Evaluation

We provide a script to evaluate the performance of a human. This script can be run in a Spyder IDE such that the live renders are visualised step by step. Further instructions are provided under `./saramis/nav_rl/eval/human_eval_instructions.txt`.

```bash
python ./saramis/nav_rl/eval/human_eval.py
```

