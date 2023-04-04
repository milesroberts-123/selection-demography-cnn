This workflow trains a convolutional neural network using population genetics data simulated with SLiM. 

My specific purpose is to train a model that can predict demographic parameters and parameters for the distribution of fitness effects at a locus.

# How to replicate my results

## 0. Set-up workflow

```
# clone repo
git clone https://github.com/milesroberts-123/selection-demography-cnn.git

# go to source code folder
cd src
```

## 1. Create table of simulation parameters

`Rscript s00_createParamTable.R`

## 2. Run simulations and train neural network on outputs

`sbatch s01_snakemake.bash`

# How to use a different SLiM model

Just replace the script in `workflow/scripts/simulation.slim` with your own SLiM script. Your new script must be named `simulation.slim`.

# To-do

- [x] add rule for fitting neural network

- [ ] add a burn-in period

- [ ] remove multiallelic sites

- [ ] perform hierarchical clustering of genotypes before image generation

- [ ] re-write neural network as a function with hyperparameters

- [ ] add a table of hyperparameters combinations to test for neural network

- [ ] calculate realized selection coefficient for each gene (due to sampling error, the actual selection coefficient in a gene might not be the same as the distribution it was drawn from)



