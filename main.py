import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
text = "Hey There! My name is Amit Chaudhary"

#tokens: [25216, 3274, 0, 3673, 1308, 382, 136538, 37219, 115904, 815]
tokens = enc.encode(text)

decoded = enc.decode(tokens)
print(f"tokens: {tokens}")
print(f"decoded: {decoded}")