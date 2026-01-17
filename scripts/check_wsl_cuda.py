#!/usr/bin/env python3
"""
WSL CUDA Environment Checker for ChatVLMLLM

This script checks if your WSL2 environment is properly configured
for running CUDA-enabled Docker containers.

Usage:
    python scripts/check_wsl_cuda.py
"""

import os
import sys
import subprocess
import shutil
from typing import Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")


def print_check(name: str, passed: bool, details: str = ""):
    """Print check result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details:
        print(f"         {Colors.YELLOW}{details}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ{Colors.END} {text}")


def run_command(cmd: str, timeout: int = 30) -> Tuple[bool, str]:
    """Run a shell command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_wsl() -> bool:
    """Check if running in WSL"""
    return os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower()


def check_wsl_version() -> Tuple[bool, str]:
    """Check WSL version (WSL2 required for GPU)"""
    if not check_wsl():
        return True, "Not running in WSL"
    
    success, output = run_command("cat /proc/version")
    if 'WSL2' in output or 'microsoft-standard' in output.lower():
        return True, "WSL2 detected"
    return False, "WSL1 detected (WSL2 required for GPU)"


def check_nvidia_driver() -> Tuple[bool, str]:
    """Check NVIDIA driver availability"""
    # Check nvidia-smi
    if shutil.which('nvidia-smi'):
        success, output = run_command("nvidia-smi --query-gpu=name,driver_version --format=csv,noheader")
        if success:
            return True, output.split('\n')[0]
    return False, "nvidia-smi not found or not working"


def check_cuda_version() -> Tuple[bool, str]:
    """Check CUDA version"""
    success, output = run_command("nvidia-smi --query-gpu=driver_version --format=csv,noheader")
    if success:
        # Try to get CUDA version from nvidia-smi
        success2, output2 = run_command("nvidia-smi | grep 'CUDA Version'")
        if success2:
            import re
            match = re.search(r'CUDA Version:\s*([\d.]+)', output2)
            if match:
                return True, f"CUDA {match.group(1)}"
    
    # Alternative: check nvcc
    if shutil.which('nvcc'):
        success, output = run_command("nvcc --version")
        if success:
            import re
            match = re.search(r'release ([\d.]+)', output)
            if match:
                return True, f"CUDA {match.group(1)}"
    
    return False, "CUDA not detected"


def check_docker() -> Tuple[bool, str]:
    """Check Docker installation"""
    if not shutil.which('docker'):
        return False, "Docker not found"
    
    success, output = run_command("docker --version")
    if success:
        return True, output
    return False, "Docker not working"


def check_docker_compose() -> Tuple[bool, str]:
    """Check Docker Compose installation"""
    # Check docker compose (v2)
    success, output = run_command("docker compose version")
    if success:
        return True, output
    
    # Check docker-compose (v1)
    if shutil.which('docker-compose'):
        success, output = run_command("docker-compose --version")
        if success:
            return True, output
    
    return False, "Docker Compose not found"


def check_nvidia_docker() -> Tuple[bool, str]:
    """Check NVIDIA Container Toolkit"""
    # Check for nvidia-container-toolkit
    success, output = run_command("which nvidia-container-toolkit")
    if success:
        return True, "nvidia-container-toolkit installed"
    
    # Alternative check via docker
    success, output = run_command("docker info 2>/dev/null | grep -i nvidia")
    if success and 'nvidia' in output.lower():
        return True, "NVIDIA runtime available in Docker"
    
    # Check nvidia-docker2
    success, output = run_command("dpkg -l | grep nvidia-docker2")
    if success:
        return True, "nvidia-docker2 installed"
    
    return False, "NVIDIA Container Toolkit not found"


def check_gpu_in_docker() -> Tuple[bool, str]:
    """Test GPU access from Docker"""
    cmd = 'docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null'
    success, output = run_command(cmd, timeout=120)
    if success:
        return True, output.split('\n')[0]
    return False, "Could not access GPU from Docker container"


def check_gpu_memory() -> Tuple[bool, str]:
    """Check available GPU memory"""
    success, output = run_command("nvidia-smi --query-gpu=memory.total,memory.free --format=csv,noheader,nounits")
    if success:
        try:
            total, free = map(int, output.split('\n')[0].split(', '))
            total_gb = total / 1024
            free_gb = free / 1024
            return True, f"Total: {total_gb:.1f} GB, Free: {free_gb:.1f} GB"
        except:
            pass
    return False, "Could not determine GPU memory"


def check_python_torch() -> Tuple[bool, str]:
    """Check PyTorch CUDA support (if installed locally)"""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            return True, f"PyTorch CUDA OK ({device_name})"
        return False, "PyTorch installed but CUDA not available"
    except ImportError:
        return True, "PyTorch not installed locally (OK for Docker)"


def get_recommended_models(vram_gb: float) -> list:
    """Get recommended models based on VRAM"""
    recommendations = []
    
    if vram_gb >= 24:
        recommendations.append("Qwen3-VL 8B @ FP16 (все модели доступны)")
    elif vram_gb >= 16:
        recommendations.append("Qwen3-VL 8B @ INT8")
        recommendations.append("Qwen3-VL 4B @ FP16")
    elif vram_gb >= 12:
        recommendations.append("Qwen3-VL 4B @ FP16")
        recommendations.append("Qwen3-VL 8B @ INT4")
    elif vram_gb >= 8:
        recommendations.append("Qwen3-VL 4B @ INT8")
        recommendations.append("Qwen3-VL 2B @ FP16")
        recommendations.append("GOT-OCR 2.0 @ FP16")
    elif vram_gb >= 6:
        recommendations.append("Qwen3-VL 2B @ FP16")
        recommendations.append("Qwen3-VL 4B @ INT4")
    elif vram_gb >= 4:
        recommendations.append("GOT-OCR 2.0 @ FP16")
        recommendations.append("Qwen3-VL 2B @ INT4")
    else:
        recommendations.append("Недостаточно VRAM для VLM моделей")
    
    return recommendations


def main():
    """Main function"""
    print_header("ChatVLMLLM - WSL CUDA Environment Check")
    
    all_passed = True
    vram_gb = 0
    
    # Check 1: WSL Version
    print("\n📋 System Environment:")
    is_wsl = check_wsl()
    if is_wsl:
        passed, details = check_wsl_version()
        print_check("WSL Version", passed, details)
        all_passed = all_passed and passed
    else:
        print_info("Not running in WSL (native Linux or other)")
    
    # Check 2: NVIDIA Driver
    print("\n🎮 NVIDIA Driver:")
    passed, details = check_nvidia_driver()
    print_check("NVIDIA Driver", passed, details)
    all_passed = all_passed and passed
    
    if passed:
        # Check CUDA version
        passed_cuda, cuda_details = check_cuda_version()
        print_check("CUDA Version", passed_cuda, cuda_details)
        
        # Check GPU memory
        passed_mem, mem_details = check_gpu_memory()
        print_check("GPU Memory", passed_mem, mem_details)
        if passed_mem:
            try:
                vram_gb = float(mem_details.split(':')[1].split('GB')[0].strip())
            except:
                pass
    
    # Check 3: Docker
    print("\n🐳 Docker:")
    passed, details = check_docker()
    print_check("Docker Installation", passed, details)
    all_passed = all_passed and passed
    
    passed, details = check_docker_compose()
    print_check("Docker Compose", passed, details)
    all_passed = all_passed and passed
    
    # Check 4: NVIDIA Container Toolkit
    print("\n📦 NVIDIA Container Toolkit:")
    passed, details = check_nvidia_docker()
    print_check("NVIDIA Container Toolkit", passed, details)
    all_passed = all_passed and passed
    
    # Check 5: GPU in Docker (only if all previous checks passed)
    if all_passed:
        print("\n🔧 Docker GPU Access (this may take a moment...):")
        passed, details = check_gpu_in_docker()
        print_check("GPU Access in Docker", passed, details)
        all_passed = all_passed and passed
    
    # Check 6: Local PyTorch (optional)
    print("\n🐍 Local Python (optional):")
    passed, details = check_python_torch()
    print_check("PyTorch CUDA", passed, details)
    
    # Summary
    print_header("Summary")
    
    if all_passed:
        print(f"\n{Colors.GREEN}✓ All checks passed!{Colors.END}")
        print(f"\n{Colors.BOLD}You can build and run the CUDA container:{Colors.END}")
        print(f"\n  {Colors.BLUE}# Build the image{Colors.END}")
        print(f"  docker compose -f docker-compose.cuda.yml build")
        print(f"\n  {Colors.BLUE}# Start the container{Colors.END}")
        print(f"  docker compose -f docker-compose.cuda.yml up -d")
        print(f"\n  {Colors.BLUE}# View logs{Colors.END}")
        print(f"  docker compose -f docker-compose.cuda.yml logs -f")
        
        # Model recommendations
        if vram_gb > 0:
            print_header("Recommended Models")
            recommendations = get_recommended_models(vram_gb)
            for rec in recommendations:
                print(f"  • {rec}")
    else:
        print(f"\n{Colors.RED}✗ Some checks failed!{Colors.END}")
        print(f"\n{Colors.BOLD}Please fix the issues above before proceeding.{Colors.END}")
        print(f"\n{Colors.YELLOW}Common fixes:{Colors.END}")
        print("""
  1. Install NVIDIA GPU driver for Windows (for WSL2):
     https://www.nvidia.com/Download/index.aspx

  2. Enable WSL2 GPU support:
     - Update Windows to build 21H2 or later
     - Update WSL: wsl --update

  3. Install NVIDIA Container Toolkit in WSL:
     curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
     curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \\
       sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \\
       sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
     sudo apt-get update
     sudo apt-get install -y nvidia-container-toolkit
     sudo nvidia-ctk runtime configure --runtime=docker
     sudo systemctl restart docker

  4. For Docker Desktop users:
     - Ensure 'Use the WSL 2 based engine' is enabled
     - Enable GPU support in Docker Desktop settings
""")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
