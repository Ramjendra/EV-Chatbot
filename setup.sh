#!/usr/bin/env bash
# =============================================================================
#  SHARP EV AI Chatbot — Automated Setup & Launcher
#  Supports: Ubuntu / Debian / Amazon Linux / macOS
#  Usage   : bash setup.sh
# =============================================================================
set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m';  GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m';  BOLD='\033[1m';  NC='\033[0m'

ok()    { echo -e "${GREEN}  ✓  $*${NC}"; }
info()  { echo -e "${CYAN}  →  $*${NC}"; }
warn()  { echo -e "${YELLOW}  ⚠  $*${NC}"; }
err()   { echo -e "${RED}  ✗  $*${NC}"; exit 1; }
step()  { echo -e "\n${BOLD}${BLUE}━━━━  $*  ━━━━${NC}\n"; }
ask()   { echo -e "${YELLOW}  ?  $*${NC}"; }

# ── Project root (dir where this script lives) ────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POC_DIR="$SCRIPT_DIR/poc"
VENV_DIR="$SCRIPT_DIR/.venv"
ENV_FILE="$POC_DIR/.env"
PYTHON_MIN="3.10"

# =============================================================================
# BANNER
# =============================================================================
banner() {
clear
echo -e "${RED}"
cat << 'EOF'
  ███████╗██╗  ██╗ █████╗ ██████╗ ██████╗
  ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗
  ███████╗███████║███████║██████╔╝██████╔╝
  ╚════██║██╔══██║██╔══██║██╔══██╗██╔═══╝
  ███████║██║  ██║██║  ██║██║  ██║██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝
EOF
echo -e "${NC}"
echo -e "  ${BOLD}EV AI Chatbot  —  Automated Setup & Launcher${NC}"
echo -e "  ${CYAN}Amazon Kendra · Bedrock Claude 3 · Transcribe · Polly · Rekognition${NC}"
echo -e "  ${CYAN}Multi-modal RAG: Text + Voice + Image${NC}"
echo ""
echo -e "  ${BOLD}Project :${NC} $SCRIPT_DIR"
echo -e "  ${BOLD}Date    :${NC} $(date '+%Y-%m-%d %H:%M')"
echo ""
}

# =============================================================================
# STEP 1 — System info + GPU detection
# =============================================================================
detect_system() {
    step "System Detection"

    # OS
    OS="unknown"
    if   [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if   command -v apt-get &>/dev/null; then OS="debian"
        elif command -v yum     &>/dev/null; then OS="rhel"
        elif command -v dnf     &>/dev/null; then OS="rhel"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then OS="macos"
    fi
    ok "OS: $OSTYPE  (package manager: $OS)"

    # CPU
    if command -v nproc &>/dev/null; then
        CPU_CORES=$(nproc)
    else
        CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "?")
    fi
    ok "CPU: $CPU_CORES cores"

    # RAM
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        RAM_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
        ok "RAM: ${RAM_GB} GB"
    fi

    # GPU detection
    GPU_DETECTED=false
    if command -v nvidia-smi &>/dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || true)
        if [[ -n "$GPU_INFO" ]]; then
            GPU_DETECTED=true
            GPU_COUNT=$(nvidia-smi --list-gpus 2>/dev/null | wc -l)
            echo -e "${GREEN}  ✓  GPU detected (${GPU_COUNT} device(s)):${NC}"
            while IFS= read -r line; do
                echo -e "        ${CYAN}▸ $line${NC}"
            done <<< "$GPU_INFO"
            # CUDA version
            CUDA_VER=$(nvidia-smi 2>/dev/null | grep -oP 'CUDA Version: \K[0-9.]+' || echo "unknown")
            ok "CUDA Version: $CUDA_VER"
        fi
    else
        warn "No NVIDIA GPU detected — running in CPU mode"
        warn "App uses Amazon Bedrock (cloud API), so GPU is not required."
    fi

    export OS GPU_DETECTED
}

# =============================================================================
# STEP 2 — Install system packages
# =============================================================================
install_system_packages() {
    step "System Packages"

    PACKAGES="python3 python3-pip python3-venv curl git unzip"

    case "$OS" in
        debian)
            info "Updating apt and installing packages..."
            sudo apt-get update -qq
            sudo apt-get install -y $PACKAGES python3-dev build-essential ffmpeg libsndfile1 2>/dev/null || \
            sudo apt-get install -y $PACKAGES 2>/dev/null
            ;;
        rhel)
            info "Installing packages via yum/dnf..."
            sudo yum install -y python3 python3-pip curl git unzip 2>/dev/null || \
            sudo dnf install -y python3 python3-pip curl git unzip 2>/dev/null
            ;;
        macos)
            if ! command -v brew &>/dev/null; then
                warn "Homebrew not found. Installing..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/homebrew/install/HEAD/install.sh)"
            fi
            brew install python@3.11 ffmpeg 2>/dev/null || true
            ;;
        *)
            warn "Unknown OS — skipping system package install. Ensure Python $PYTHON_MIN+ is available."
            ;;
    esac

    # AWS CLI
    if ! command -v aws &>/dev/null; then
        info "Installing AWS CLI v2..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
            unzip -q /tmp/awscliv2.zip -d /tmp/awscli
            sudo /tmp/awscli/aws/install --update
            rm -rf /tmp/awscliv2.zip /tmp/awscli
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install awscli 2>/dev/null || true
        fi
        ok "AWS CLI installed: $(aws --version 2>&1 | head -1)"
    else
        ok "AWS CLI already installed: $(aws --version 2>&1 | head -1)"
    fi
}

# =============================================================================
# STEP 3 — Python version check
# =============================================================================
check_python() {
    step "Python Environment"

    PYTHON_BIN=""
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            VER=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            MAJOR=${VER%%.*}; MINOR=${VER##*.}
            REQ_MINOR=${PYTHON_MIN##*.}
            if [[ "$MAJOR" -ge 3 && "$MINOR" -ge "$REQ_MINOR" ]]; then
                PYTHON_BIN="$cmd"
                ok "Python $VER found at: $(command -v $cmd)"
                break
            fi
        fi
    done

    [[ -z "$PYTHON_BIN" ]] && err "Python $PYTHON_MIN+ required. Install it and re-run this script."
    export PYTHON_BIN
}

# =============================================================================
# STEP 4 — Virtual environment
# =============================================================================
setup_venv() {
    step "Virtual Environment"

    if [[ -d "$VENV_DIR" ]]; then
        ok "Virtual environment already exists: $VENV_DIR"
    else
        info "Creating virtual environment at $VENV_DIR ..."
        "$PYTHON_BIN" -m venv "$VENV_DIR"
        ok "Virtual environment created"
    fi

    # Activate
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    ok "Activated: $(python --version)"

    # Upgrade pip
    info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel -q
    ok "pip $(pip --version | awk '{print $2}')"
}

# =============================================================================
# STEP 5 — Install Python dependencies
# =============================================================================
install_python_deps() {
    step "Python Dependencies"

    info "Installing from poc/requirements.txt ..."
    pip install -r "$POC_DIR/requirements.txt" -q
    ok "Core dependencies installed"

    # GPU extras: install torch if GPU detected (for potential local inference)
    if [[ "$GPU_DETECTED" == "true" ]]; then
        info "GPU detected — installing PyTorch (CUDA) for optional local inference..."
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 -q 2>/dev/null || \
        pip install torch torchvision -q 2>/dev/null || \
        warn "PyTorch install skipped (not required for Bedrock-based pipeline)"
    fi

    # Script-generation extras
    info "Installing python-docx for document generation scripts..."
    pip install python-docx -q
    ok "python-docx installed"

    # Show installed versions
    echo ""
    echo -e "  ${BOLD}Installed packages:${NC}"
    pip show boto3 streamlit python-dotenv 2>/dev/null | grep -E "^(Name|Version)" | \
        awk 'NR%2==1{name=$2} NR%2==0{printf "        %-20s %s\n", name, $2}'
}

# =============================================================================
# STEP 6 — AWS credentials check
# =============================================================================
check_aws_credentials() {
    step "AWS Credentials"

    if aws sts get-caller-identity &>/dev/null; then
        ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        USER=$(aws sts get-caller-identity --query Arn --output text)
        REGION=$(aws configure get region 2>/dev/null || echo "not set")
        ok "AWS authenticated"
        echo -e "        Account : ${CYAN}$ACCOUNT${NC}"
        echo -e "        Identity: ${CYAN}$USER${NC}"
        echo -e "        Region  : ${CYAN}$REGION${NC}"

        # Warn if region is not Tokyo
        if [[ "$REGION" != "ap-northeast-1" ]]; then
            warn "Recommended region for SHARP EV POC is ap-northeast-1 (Tokyo)"
            ask "Set region to ap-northeast-1? [y/N]"
            read -r SET_REGION
            if [[ "$SET_REGION" =~ ^[Yy]$ ]]; then
                aws configure set region ap-northeast-1
                ok "Region set to ap-northeast-1"
            fi
        fi
    else
        warn "AWS credentials not configured."
        echo ""
        echo -e "  ${BOLD}Configure now:${NC}"
        echo -e "  ${CYAN}  aws configure${NC}"
        echo ""
        echo -e "  You need:"
        echo -e "    AWS Access Key ID"
        echo -e "    AWS Secret Access Key"
        echo -e "    Default region: ap-northeast-1"
        echo ""
        ask "Run 'aws configure' now? [y/N]"
        read -r DO_CONFIG
        if [[ "$DO_CONFIG" =~ ^[Yy]$ ]]; then
            aws configure
        else
            warn "Skipping AWS config. Set credentials before running the app."
        fi
    fi
}

# =============================================================================
# STEP 7 — Environment file setup
# =============================================================================
setup_env_file() {
    step "Environment Configuration (.env)"

    if [[ -f "$ENV_FILE" ]]; then
        ok ".env file already exists"
        # Load and show current values (masking secrets)
        source "$ENV_FILE" 2>/dev/null || true
        echo -e "  ${BOLD}Current values:${NC}"
        echo -e "    AWS_REGION      : ${CYAN}${AWS_REGION:-not set}${NC}"
        echo -e "    S3_BUCKET_NAME  : ${CYAN}${S3_BUCKET_NAME:-not set}${NC}"
        echo -e "    KENDRA_INDEX_ID : ${CYAN}${KENDRA_INDEX_ID:-not set}${NC}"
    else
        info "Creating .env from .env.example ..."
        cp "$POC_DIR/.env.example" "$ENV_FILE"

        # Auto-detect region from AWS config
        DETECTED_REGION=$(aws configure get region 2>/dev/null || echo "ap-northeast-1")

        # Prompt for values
        echo ""
        ask "AWS Region [${DETECTED_REGION}]:"
        read -r INPUT_REGION
        REGION_VAL="${INPUT_REGION:-$DETECTED_REGION}"

        ask "S3 Bucket name [sharp-ev-kendra-poc-docs]:"
        read -r INPUT_BUCKET
        BUCKET_VAL="${INPUT_BUCKET:-sharp-ev-kendra-poc-docs}"

        ask "Kendra Index ID (leave blank if not yet created):"
        read -r INPUT_INDEX_ID

        # Write .env
        cat > "$ENV_FILE" << ENVEOF
AWS_REGION=${REGION_VAL}
AWS_PROFILE=default
S3_BUCKET_NAME=${BUCKET_VAL}
KENDRA_INDEX_ID=${INPUT_INDEX_ID:-}
ENVEOF
        ok ".env created at $ENV_FILE"
    fi
}

# =============================================================================
# STEP 8 — Run setup_kendra.py
# =============================================================================
run_kendra_setup() {
    step "Kendra Infrastructure Setup"
    info "Running setup_kendra.py — this creates S3 bucket, IAM role, and Kendra index."
    warn "Note: Kendra index activation takes ~20–30 minutes on first creation."
    echo ""
    cd "$POC_DIR"
    python setup_kendra.py
    ok "Kendra setup complete"
    cd "$SCRIPT_DIR"
}

# =============================================================================
# STEP 9 — Ingest documents
# =============================================================================
run_ingest() {
    step "Document Ingestion"
    DOCS_DIR="$POC_DIR/docs"
    info "Ingesting documents from $DOCS_DIR into Kendra..."
    cd "$POC_DIR"
    python ingest.py --docs "$DOCS_DIR"
    ok "Documents ingested"
    cd "$SCRIPT_DIR"
}

# =============================================================================
# STEP 10 — Launch Streamlit app
# =============================================================================
launch_app() {
    step "Launching SHARP EV Chatbot"
    echo ""
    echo -e "  ${BOLD}${GREEN}Starting Streamlit app...${NC}"
    echo -e "  ${CYAN}URL: http://localhost:8501${NC}"
    echo -e "  ${CYAN}Press Ctrl+C to stop${NC}"
    echo ""
    cd "$POC_DIR"
    streamlit run app.py \
        --server.port 8501 \
        --server.headless false \
        --browser.gatherUsageStats false \
        --theme.primaryColor "#1F497D" \
        --theme.backgroundColor "#F4F7FB" \
        --theme.secondaryBackgroundColor "#FFFFFF" \
        --theme.textColor "#1A1A2E"
}

# =============================================================================
# MAIN MENU
# =============================================================================
show_menu() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  Setup Menu${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${GREEN}[1]${NC}  🚀  Full Setup + Launch    (recommended for first run)"
    echo -e "  ${GREEN}[2]${NC}  ☁️   Setup Kendra Index     (one-time, ~30 min)"
    echo -e "  ${GREEN}[3]${NC}  📄  Ingest Documents       (upload docs to Kendra)"
    echo -e "  ${GREEN}[4]${NC}  💬  Launch Chatbot         (start Streamlit app)"
    echo -e "  ${GREEN}[5]${NC}  🔧  Reinstall Dependencies (fix broken packages)"
    echo -e "  ${GREEN}[6]${NC}  ✅  Check System Status"
    echo -e "  ${RED}[0]${NC}  ❌  Exit"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    ask "Select option [1]:"
    read -r CHOICE
    CHOICE="${CHOICE:-1}"
}

check_status() {
    step "System Status Check"

    # venv
    [[ -d "$VENV_DIR" ]] && ok "Virtual environment: $VENV_DIR" || warn "Virtual environment: NOT FOUND"

    # .env
    [[ -f "$ENV_FILE" ]] && ok ".env file: $ENV_FILE" || warn ".env file: NOT FOUND"

    # AWS
    if aws sts get-caller-identity &>/dev/null; then
        ok "AWS credentials: valid ($(aws sts get-caller-identity --query Account --output text))"
    else
        warn "AWS credentials: NOT CONFIGURED"
    fi

    # Kendra index ID
    source "$ENV_FILE" 2>/dev/null || true
    if [[ -n "${KENDRA_INDEX_ID:-}" ]]; then
        ok "Kendra Index ID: $KENDRA_INDEX_ID"
        # Check index status
        STATUS=$(aws kendra describe-index --id "$KENDRA_INDEX_ID" \
                 --region "${AWS_REGION:-ap-northeast-1}" \
                 --query Status --output text 2>/dev/null || echo "UNKNOWN")
        echo -e "        Status: ${CYAN}$STATUS${NC}"
    else
        warn "Kendra Index ID: NOT SET (run option 2)"
    fi

    # Python packages
    if [[ -d "$VENV_DIR" ]]; then
        source "$VENV_DIR/bin/activate"
        echo ""
        echo -e "  ${BOLD}Package versions:${NC}"
        for pkg in boto3 streamlit python-dotenv Pillow; do
            VER=$(pip show "$pkg" 2>/dev/null | grep ^Version | awk '{print $2}' || echo "NOT INSTALLED")
            if [[ "$VER" == "NOT INSTALLED" ]]; then
                warn "  $pkg: $VER"
            else
                ok "  $pkg: $VER"
            fi
        done
    fi

    # GPU
    if command -v nvidia-smi &>/dev/null; then
        GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        ok "GPU: $GPU"
    else
        info "GPU: Not available (not required)"
    fi
}

# =============================================================================
# ENTRY POINT
# =============================================================================
main() {
    banner
    detect_system
    check_python
    setup_venv

    # Always activate venv
    source "$VENV_DIR/bin/activate"

    show_menu

    case "$CHOICE" in
        1)  # Full setup + launch
            install_system_packages
            install_python_deps
            check_aws_credentials
            setup_env_file
            source "$ENV_FILE" 2>/dev/null || true
            if [[ -z "${KENDRA_INDEX_ID:-}" ]]; then
                ask "Setup Kendra index now? (~30 min) [y/N]:"
                read -r DO_KENDRA
                [[ "$DO_KENDRA" =~ ^[Yy]$ ]] && run_kendra_setup
            fi
            ask "Ingest sample documents? [Y/n]:"
            read -r DO_INGEST
            [[ ! "$DO_INGEST" =~ ^[Nn]$ ]] && run_ingest
            launch_app
            ;;
        2)  run_kendra_setup ;;
        3)  run_ingest ;;
        4)  launch_app ;;
        5)  install_python_deps ;;
        6)  check_status ;;
        0)  echo -e "\n${CYAN}  Goodbye!${NC}\n"; exit 0 ;;
        *)  warn "Invalid option. Launching app directly..."; launch_app ;;
    esac
}

main "$@"
