CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -Wpedantic
TARGET := eff
SRC := main.cpp

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)
