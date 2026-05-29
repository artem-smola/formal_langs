TEX = xelatex
TEXFLAGS = -interaction=nonstopmode -halt-on-error
TARGET = report

.PHONY: all clean

all: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex
	$(TEX) $(TEXFLAGS) $(TARGET).tex
	$(TEX) $(TEXFLAGS) $(TARGET).tex

clean:
	rm -f $(TARGET).aux $(TARGET).log $(TARGET).out $(TARGET).pdf
