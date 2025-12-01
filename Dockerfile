# 1. Use an official Python base image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /main

# 3. Copy dependency list first (for caching)
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code
COPY . .

# 6. Run your application
CMD ["python", "main.py"]
