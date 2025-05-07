FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     curl     && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -sSf https://install.ultraviolet.dev | sh
ENV PATH="/root/.cargo/bin:/e/projects/ph/backend/.venv/Scripts:/e/Anaconda/condabin:/c/Users/sa268/bin:/mingw64/bin:/usr/local/bin:/usr/bin:/usr/bin:/mingw64/bin:/usr/bin:/c/Users/sa268/bin:/c/Program Files/Microsoft MPI/Bin:/c/Program Files (x86)/Microsoft SDKs/Azure/CLI2/wbin:/c/Python312/Scripts:/c/Python312:/c/Program Files (x86)/Common Files/Oracle/Java/javapath:/c/Program Files (x86)/Common Files/Intel/Shared Libraries/redist/intel64/compiler:/c/Program Files (x86)/VMware/VMware Player/bin:/c/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.1/bin:/c/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.1/libnvvp:/c/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin:/c/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/libnvvp:/c/oraclexe/app/oracle/product/11.2.0/server/bin:/c/Program Files/Common Files/Oracle/Java/javapath:/c/Program Files/ImageMagick-7.1.0-Q16-HDRI:/c/Windows/system32:/c/Windows:/c/Windows/System32/Wbem:/c/Windows/System32/WindowsPowerShell/v1.0:/c/Windows/System32/OpenSSH:/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common:/cmd:/c/Program Files/dotnet:/c/Program Files/NVIDIA Corporation/Nsight Compute 2023.1.0:/c/path_prgs/ffmpeg/bin:/c/Program Files (x86)/sox-14-4-2:/c/Program Files/nodejs:/c/ProgramData/chocolatey/bin:/c/Android:/c/Users/sa268/AppData/Local/Programs/cursor/resources/app/bin:/c/WINDOWS/system32:/c/WINDOWS:/c/WINDOWS/System32/Wbem:/c/WINDOWS/System32/WindowsPowerShell/v1.0:/c/WINDOWS/System32/OpenSSH:/c/WINDOWS/system32:/c/Program Files/Rancher Desktop/resources/resources/win32/bin:/c/Program Files/Rancher Desktop/resources/resources/win32/docker-cli-plugins:/c/Program Files/Rancher Desktop/resources/resources/linux/bin:/c/Program Files/Rancher Desktop/resources/resources/linux/docker-cli-plugins:/c/Program Files/Docker/Docker/resources/bin:/c/Program Files/NVIDIA Corporation/NVIDIA app/NvDLISR:/c/Program Files/Inkscape/bin:/c/Users/sa268/.local/share/solana/install/active_release/bin:/c/Users/sa268/AppData/Local/Microsoft/WindowsApps:/c/Users/sa268/AppData/Local/Programs/Microsoft VS Code/bin:/e/Anaconda/Scripts:/c/Program Files/heroku/bin:/c/Users/sa268/AppData/Local/gitkraken/bin:/c/Program Files/Java/jdk-17.0.2/bin:/c/Program Files/MongoDB/Server/5.0/bin:/c/Users/sa268/Downloads/ngrok-v3-stable-windows-amd64:/c/sqlite:/e/JetBrains Rider 2023.2.1/bin:/c/Users/sa268/AppData/Roaming/npm:/c/Users/sa268/AppData/Local/Programs/Ollama:/c/Users/sa268/AppData/Local/JetBrains/Toolbox/scripts:/c/Users/sa268/AppData/Local/Microsoft/WindowsApps:/c/Users/sa268/AppData/Local/Programs/cursor/resources/app/bin:/c/Users/sa268/AppData/Roaming/Code/User/globalStorage/github.copilot-chat/debugCommand:/usr/bin/vendor_perl:/usr/bin/core_perl"

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
