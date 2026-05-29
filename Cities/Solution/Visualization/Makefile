PYTHON := python3

.PHONY: all png clean

all:
	$(PYTHON) generate_visualizations.py

png:
	$(PYTHON) generate_visualizations.py --require-dot

clean:
	rm -f test*.dot test*.png
