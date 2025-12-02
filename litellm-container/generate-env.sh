#!/bin/bash
# generate-env.sh - Generate .env file for LiteLLM

MASTER_KEY="sk-litellm-master-$(openssl rand -hex 16)"
SALT_KEY="sk-litellm-salt-$(openssl rand -hex 16)"

cat > .env << EOF
# LiteLLM Required Keys
LITELLM_MASTER_KEY=${MASTER_KEY}
LITELLM_SALT_KEY=${SALT_KEY}

# Database (optional - has default)
# POSTGRES_PASSWORD=dbpassword9090

# LLM Provider API Keys (add as needed)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GEMINI_API_KEY=
# GROQ_API_KEY=
# MISTRAL_API_KEY=
# COHERE_API_KEY=
# AZURE_API_KEY=
# AZURE_API_BASE=
EOF

echo "✅ Generated .env file with keys:"
echo "MASTER_KEY: ${MASTER_KEY}"
echo "SALT_KEY: ${SALT_KEY}"
