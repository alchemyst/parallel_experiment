targets := $(addsuffix .out,$(basename $(wildcard data/*)))

all: $(targets)

data/%.out: data/%.inp
	python runner.py $@

clean:
	-rm $(targets)

.PHONY: clean
