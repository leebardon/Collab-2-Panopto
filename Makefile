.PHONY: lint clean active deactive empty

CONDA_BASE=$(conda info --base)

clean: 
	@find . -regex '^.*\(__pycache__\|\.py[co]\)' -delete
	 

lint:
	@black *.py . src 

active:
	@eval "$(conda shell.bash hook)"
	@conda activate collaborate-to-panopto

deactive:
	@conda deactivate

# Empties the downloads and reports folder of all files except hidden ones such as .gitkeep
empty:
	@rm -r .logs/*
	@rm -r reports/*
	@rm -r downloads/* 
