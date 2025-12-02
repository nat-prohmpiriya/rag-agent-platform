# RAG Agent Platform - Project Specification

## 📋 Document Info

| | |
|--|--|
| **Version** | 2.0 |
| **Date** | December 2024 |
| **Author** | - |
| **Status** | Ready for Development |
| **Changes** | Added Fine-tuning Module + Text-to-SQL |

---

## 🎯 Project Overview

| | |
|--|--|
| **Project Name** | RAG Agent Platform |
| **Type** | Domain-Agnostic RAG + Multi-Agent System |
| **Purpose** | Portfolio สำหรับสมัครงาน AI Developer |
| **Target Company** | Sciology (Mental Health/Scientific Research) |

### Key Differentiators

- **Domain-Agnostic**: เปลี่ยน domain ด้วย config file
- **Multi-Agent**: Pre-built agents สำหรับ HR, Legal, Finance, Research
- **Multi-Project**: แยก knowledge base ตาม project
- **Text-to-SQL**: Query database ด้วยภาษาธรรมชาติ ⭐ NEW
- **Fine-tuning**: Train custom embeddings/models ⭐ NEW
- **Production-Ready**: User management, usage limits, monitoring

---

## 🛠 Tech Stack

### Core Technologies

| Layer | Technology | Reason |
|-------|------------|--------|
| **Frontend** | SvelteKit (Static) | เร็ว, รวม container เดียวกับ backend |
| **Backend** | FastAPI (Python) | Async, เหมาะกับ AI/ML |
| **LLM Gateway** | LiteLLM (Library + Proxy) | Unified API, multi-provider, Admin UI |
| **Vector Store** | ChromaDB | Embedded, ง่าย, lightweight |
| **Embeddings** | Sentence-transformers | Open-source, fine-tunable |
| **Agent Framework** | Custom + LangGraph | เริ่มทำเอง แล้ว upgrade |
| **Monitoring** | Prometheus | Metrics collection |
| **Database** | PostgreSQL | User data, conversations |

### NEW: Fine-tuning Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Training** | Hugging Face Transformers | Fine-tune models |
| **Optimization** | PEFT / LoRA | Efficient fine-tuning |
| **Tracking** | Weights & Biases (optional) | Experiment tracking |
| **Model Hub** | Hugging Face Hub | Store & share models |
| **Local Inference** | Ollama | Run fine-tuned models |

### NEW: Text-to-SQL Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **SQL Generation** | LLM + Schema Context | Generate SQL from text |
| **DB Connectors** | SQLAlchemy | Connect to multiple DBs |
| **Query Execution** | Secure sandbox | Safe query execution |
| **Result Formatting** | Pandas | Format & visualize results |

### DevOps & Infrastructure

| Component | Technology |
|-----------|------------|
| **VPS** | Hetzner CX32 (EU) |
| **PaaS** | Coolify (self-hosted) |
| **CI/CD** | GitHub Actions |
| **Container** | Docker + Docker Compose |
| **SSL** | Let's Encrypt (auto via Coolify) |
| **Version Control** | GitHub |

---

## 💰 Cost Breakdown

| Item | Cost/Month |
|------|------------|
| Hetzner CX32 (4 vCPU, 8GB RAM, 80GB SSD) | €6.80 (~฿260) |
| Coolify | Free |
| GitHub Actions | Free (2,000 min) |
| LiteLLM | Free |
| Hugging Face Hub | Free (public models) |
| Weights & Biases | Free (100GB) |
| **Infrastructure Total** | **~฿260/month** |
| LLM API (OpenAI/Claude/Groq) | Pay-per-use |

### Server Specs

```
Hetzner CX32 (EU - Germany/Finland)
- 4 vCPU (Shared, Intel)
- 8 GB RAM
- 80 GB NVMe SSD
- 20 TB Traffic included
- €6.80/month

For Fine-tuning (optional - use Colab/Kaggle):
- Google Colab Pro: $10/month (A100 GPU)
- Kaggle: Free (30h/week GPU)
```

---

## 🏗 Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hetzner VPS (CX32)                           │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                        Coolify                             ││
│  │                                                            ││
│  │  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │  App Container   │  │   LiteLLM    │  │  Prometheus  │ ││
│  │  │  ┌────────────┐  │  │   Proxy      │  │              │ ││
│  │  │  │Svelte(static)│ │  │   ┌──────┐  │  │              │ ││
│  │  │  ├────────────┤  │  │   │Admin │  │  │              │ ││
│  │  │  │  FastAPI   │──┼──┼──▶│ UI   │  │  │              │ ││
│  │  │  ├────────────┤  │  │   └──────┘  │  │              │ ││
│  │  │  │  ChromaDB  │  │  │              │  │              │ ││
│  │  │  ├────────────┤  │  │              │  │              │ ││
│  │  │  │ PostgreSQL │  │  │              │  │              │ ││
│  │  │  └────────────┘  │  └──────┬───────┘  └──────────────┘ ││
│  │  └──────────────────┘         │                           ││
│  └───────────────────────────────┼───────────────────────────┘│
└──────────────────────────────────┼─────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    LLM APIs      │    │  Customer DBs    │    │  Hugging Face    │
│ OpenAI │ Claude  │    │ PostgreSQL,MySQL │    │  Hub (Models)    │
│ Groq   │ Ollama  │    │ MSSQL, MongoDB   │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Data Flow: RAG + Text-to-SQL

```
User Query: "ยอดขายเดือนนี้เท่าไหร่ และมีเอกสาร policy อะไรเกี่ยวกับ commission"
     │
     ▼
┌─────────────────┐
│  Query Router   │  ← Classify: RAG / SQL / Both
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│  RAG  │ │ SQL   │
│Pipeline│ │Pipeline│
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Chunks │ │Query  │
│+Scores│ │Results│
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│   LLM Synthesis │  ← Combine results
└─────────────────┘
         │
         ▼
┌─────────────────┐
│    Response     │
│ "ยอดขายเดือนนี้ │
│  ฿1.2M และ...   │
└─────────────────┘
```

### Fine-tuning Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fine-tuning Pipeline                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Data Preparation                                            │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│     │ Raw Data │ ──▶ │ Process  │ ──▶ │ Dataset  │             │
│     │ (docs)   │     │ & Clean  │     │ (HF fmt) │             │
│     └──────────┘     └──────────┘     └──────────┘             │
│                                                                 │
│  2. Training                                                    │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│     │ Base     │ ──▶ │ Fine-tune│ ──▶ │ Trained  │             │
│     │ Model    │     │ (LoRA)   │     │ Model    │             │
│     └──────────┘     └──────────┘     └──────────┘             │
│                           │                                     │
│                           ▼                                     │
│                      ┌──────────┐                               │
│                      │  W&B     │  ← Track metrics              │
│                      │ Logging  │                               │
│                      └──────────┘                               │
│                                                                 │
│  3. Deployment                                                  │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│     │ Trained  │ ──▶ │ Push to  │ ──▶ │ Use in   │             │
│     │ Model    │     │ HF Hub   │     │ Platform │             │
│     └──────────┘     └──────────┘     └──────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Features Specification

### 1. User System

#### 1.1 Authentication
- [ ] User registration (email + password)
- [ ] User login / logout
- [ ] Password reset
- [ ] Session management (JWT)

#### 1.2 User Tiers

| Tier | Token Limit | Projects | Documents | Models | Rate Limit |
|------|-------------|----------|-----------|--------|------------|
| **Free** | 50K/month | 3 | 10 | GPT-3.5 | 5 req/min |
| **Pro** | 500K/month | 20 | 100 | GPT-4, Claude | 30 req/min |
| **Enterprise** | Unlimited | Unlimited | Unlimited | All + Custom | 100 req/min |

#### 1.3 User Settings
- [ ] Profile management
- [ ] Default model preference
- [ ] Notification settings
- [ ] API key management (for power users)

---

### 2. Project System

#### 2.1 Project Management
- [ ] Create / Edit / Delete projects
- [ ] Project naming & description
- [ ] Project icon/color selection
- [ ] Project archiving

#### 2.2 Project Components

| Component | Description |
|-----------|-------------|
| **Documents** | Isolated knowledge base per project |
| **Database Connections** | External DB for Text-to-SQL ⭐ NEW |
| **Conversations** | Chat history within project |
| **Agent** | Assigned agent for project |
| **Settings** | Model, temperature, custom prompts |
| **Members** | Share with team (optional) |

#### 2.3 Project Settings
- [ ] Select agent type
- [ ] Select LLM model
- [ ] Custom system prompt
- [ ] Temperature / Top-K settings
- [ ] Enable/disable features
- [ ] Database connection settings ⭐ NEW

---

### 3. Agent System

#### 3.1 Pre-built Agents

| Agent | Description | Tools |
|-------|-------------|-------|
| **General** | General-purpose assistant | RAG search, summarize |
| **HR** | HR policy & recruitment | Resume parser, policy RAG, skill matcher |
| **Legal** | Legal analysis & research | Contract analyzer, law search, case compare |
| **Finance** | Financial analysis | Financial calculator, report analyzer, **SQL query** ⭐ |
| **Research** | Research assistant | Paper search, citation finder |
| **Data Analyst** | Data analysis ⭐ NEW | **SQL query**, chart generator, data summary |

#### 3.2 Agent Configuration (YAML)

```yaml
agent:
  name: "Data Analyst"
  description: "ผู้ช่วยวิเคราะห์ข้อมูลและ query database"
  icon: "📊"
  
persona:
  system_prompt: |
    คุณเป็นนักวิเคราะห์ข้อมูล ช่วย query database และสรุปผล
    สร้าง SQL ที่ปลอดภัย ไม่ DELETE หรือ UPDATE ข้อมูล
    อธิบายผลลัพธ์เป็นภาษาที่เข้าใจง่าย

tools:
  - name: "sql_query"
    description: "Query database ด้วย SQL"
    config:
      read_only: true
      max_rows: 1000
      timeout: 30
  - name: "chart_generator"
    description: "สร้าง chart จากข้อมูล"
  - name: "rag_search"
    description: "ค้นหาจากเอกสาร"

knowledge_base:
  sources:
    - type: "local"
      path: "./data/analytics/"
    - type: "database"
      connection: "${DB_CONNECTION}"
      
ui:
  suggested_prompts:
    - "ยอดขายเดือนนี้เท่าไหร่"
    - "เปรียบเทียบยอดขาย Q1 vs Q2"
    - "Top 10 ลูกค้าที่ซื้อเยอะสุด"
```

#### 3.3 Agent Features
- [ ] Agent selector UI
- [ ] Agent thinking display (step-by-step)
- [ ] Tool execution visualization
- [ ] Custom agent creation via YAML

---

### 4. Chat System

#### 4.1 Core Chat Features
- [ ] Real-time streaming responses
- [ ] Markdown rendering
- [ ] Code syntax highlighting
- [ ] Message editing / regeneration
- [ ] Conversation branching

#### 4.2 Source Citations
- [ ] Display source documents
- [ ] Show page/section references
- [ ] Link to original document
- [ ] Confidence scores
- [ ] Show SQL query used ⭐ NEW

#### 4.3 Multi-Model Support
- [ ] Model selector dropdown
- [ ] Models: GPT-3.5, GPT-4, Claude, Llama, Ollama
- [ ] Custom fine-tuned models ⭐ NEW
- [ ] Per-conversation model switching
- [ ] Model comparison mode (A/B)

#### 4.4 Conversation Memory
- [ ] Conversation history persistence
- [ ] Context window management
- [ ] Conversation summarization (for long chats)

---

### 5. RAG System

#### 5.1 Document Processing
- [ ] Supported formats: PDF, DOCX, TXT, MD, CSV
- [ ] Automatic text extraction
- [ ] Smart chunking (semantic / recursive)
- [ ] Metadata extraction

#### 5.2 Vector Store
- [ ] ChromaDB integration
- [ ] Per-project collections
- [ ] Embedding model: multilingual-e5-base (or fine-tuned)
- [ ] Hybrid search (Dense + BM25)

#### 5.3 Retrieval Pipeline
- [ ] Query preprocessing
- [ ] Hybrid search (dense + sparse)
- [ ] Reciprocal Rank Fusion (RRF)
- [ ] Re-ranking (optional)
- [ ] Context assembly

#### 5.4 Debug Panel
- [ ] Show retrieved chunks
- [ ] Show relevance scores
- [ ] Show latency breakdown
- [ ] Show token usage

---

### 6. Text-to-SQL System ⭐ NEW

#### 6.1 Database Connections

| Database | Status | Connector |
|----------|--------|-----------|
| **PostgreSQL** | ✅ Supported | psycopg2 |
| **MySQL** | ✅ Supported | pymysql |
| **MariaDB** | ✅ Supported | pymysql |
| **SQL Server** | ✅ Supported | pyodbc |
| **SQLite** | ✅ Supported | sqlite3 |
| **MongoDB** | 🔜 Future | pymongo |

#### 6.2 Connection Management
- [ ] Add database connection (encrypted credentials)
- [ ] Test connection
- [ ] Auto-discover schema
- [ ] Schema caching
- [ ] Connection pooling

#### 6.3 Schema Configuration

```yaml
database:
  name: "Sales Database"
  type: "postgresql"
  connection:
    host: "${DB_HOST}"
    port: 5432
    database: "sales_db"
    username: "${DB_USER}"
    password: "${DB_PASS}"  # Encrypted
    
schema:
  tables:
    - name: "orders"
      description: "ตารางคำสั่งซื้อ"
      columns:
        - name: "id"
          type: "integer"
          description: "รหัสคำสั่งซื้อ"
        - name: "customer_id"
          type: "integer"
          description: "รหัสลูกค้า"
        - name: "amount"
          type: "decimal"
          description: "ยอดรวม"
        - name: "created_at"
          type: "timestamp"
          description: "วันที่สั่ง"
    
    - name: "customers"
      description: "ตารางลูกค้า"
      columns:
        - name: "id"
          type: "integer"
        - name: "name"
          type: "varchar"
        - name: "email"
          type: "varchar"

  relationships:
    - from: "orders.customer_id"
      to: "customers.id"
      type: "many-to-one"
```

#### 6.4 SQL Generation Pipeline

```
User Query: "ยอดขายเดือนนี้แยกตามลูกค้า"
     │
     ▼
┌─────────────────┐
│ Schema Context  │  ← Include table/column descriptions
│ + Query         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generate   │  ← Generate SQL
│  SQL Query      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Validator  │  ← Check syntax, safety
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute (Safe)  │  ← Read-only, timeout, row limit
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Format Results  │  ← Table, chart, summary
└─────────────────┘
```

#### 6.5 Safety Features
- [ ] Read-only mode (SELECT only)
- [ ] Query whitelist (no DROP, DELETE, UPDATE)
- [ ] Row limit (max 1000 rows)
- [ ] Timeout (30 seconds)
- [ ] Query cost estimation
- [ ] Parameterized queries (prevent SQL injection)
- [ ] Sensitive column masking (e.g., passwords)

#### 6.6 Result Visualization
- [ ] Auto-detect best visualization
- [ ] Table view (with pagination)
- [ ] Bar chart
- [ ] Line chart
- [ ] Pie chart
- [ ] Export to CSV/Excel

#### 6.7 Example Queries

| Natural Language | Generated SQL |
|------------------|---------------|
| "ยอดขายเดือนนี้" | `SELECT SUM(amount) FROM orders WHERE created_at >= '2024-12-01'` |
| "Top 5 ลูกค้า" | `SELECT c.name, SUM(o.amount) as total FROM orders o JOIN customers c ON o.customer_id = c.id GROUP BY c.id ORDER BY total DESC LIMIT 5` |
| "ออเดอร์ของ John" | `SELECT * FROM orders WHERE customer_id = (SELECT id FROM customers WHERE name LIKE '%John%')` |

---

### 7. Fine-tuning Module ⭐ NEW

#### 7.1 Fine-tuning Options

| Type | Use Case | Difficulty | Time |
|------|----------|------------|------|
| **Embedding Fine-tune** | Improve retrieval สำหรับ domain | ⭐⭐ Medium | 1-2 hours |
| **Classifier Fine-tune** | Intent classification | ⭐ Easy | 30 min |
| **LLM Fine-tune (LoRA)** | Domain-specific responses | ⭐⭐⭐ Hard | 2-4 hours |

#### 7.2 Embedding Fine-tuning

**Purpose**: ปรับปรุง retrieval quality สำหรับ domain เฉพาะ

**Base Model**: `intfloat/multilingual-e5-base`

**Training Data Format**:
```json
{
  "query": "นโยบายลาพักร้อนกี่วัน",
  "positive": "พนักงานมีสิทธิ์ลาพักร้อนปีละ 10 วัน",
  "negative": "พนักงานต้องแต่งกายสุภาพ"
}
```

**Training Script**:
```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load base model
model = SentenceTransformer('intfloat/multilingual-e5-base')

# Prepare training data
train_examples = [
    InputExample(texts=[q, pos, neg])
    for q, pos, neg in training_data
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.TripletLoss(model)

# Fine-tune
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_path='./models/custom-e5-hr'
)

# Push to Hugging Face Hub
model.push_to_hub("username/custom-e5-hr")
```

#### 7.3 Intent Classifier Fine-tuning

**Purpose**: Classify query → Agent/Tool

**Base Model**: `bert-base-multilingual-cased`

**Training Data Format**:
```json
[
  {"text": "นโยบายลาป่วย", "label": "hr"},
  {"text": "สัญญาจ้าง", "label": "legal"},
  {"text": "ยอดขายเดือนนี้", "label": "finance"},
  {"text": "paper เกี่ยวกับ AI", "label": "research"}
]
```

**Training Script**:
```python
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments, 
    Trainer
)
from datasets import Dataset

# Load base model
model_name = "bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=5  # hr, legal, finance, research, general
)

# Prepare dataset
dataset = Dataset.from_list(training_data)
dataset = dataset.map(lambda x: tokenizer(x['text'], truncation=True, padding=True))

# Training arguments
training_args = TrainingArguments(
    output_dir="./models/intent-classifier",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=True,
    hub_model_id="username/intent-classifier-th"
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer
)
trainer.train()
```

#### 7.4 LLM Fine-tuning (LoRA)

**Purpose**: Fine-tune LLM สำหรับ domain-specific responses

**Base Model**: `Qwen/Qwen2.5-7B-Instruct` หรือ `meta-llama/Llama-3.1-8B-Instruct`

**Training Data Format** (Instruction format):
```json
[
  {
    "instruction": "ตอบคำถามเกี่ยวกับนโยบาย HR",
    "input": "ลาพักร้อนได้กี่วัน",
    "output": "ตามนโยบายบริษัท พนักงานมีสิทธิ์ลาพักร้อนปีละ 10 วัน โดยต้องแจ้งล่วงหน้าอย่างน้อย 3 วัน และได้รับอนุมัติจากหัวหน้างาน"
  }
]
```

**Training with QLoRA** (Efficient fine-tuning):
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Quantization config (4-bit)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
)

# Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Prepare model
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# Train with SFTTrainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    max_seq_length=512,
    args=TrainingArguments(
        output_dir="./models/hr-assistant-lora",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        push_to_hub=True,
    )
)
trainer.train()

# Merge LoRA weights and push
merged_model = model.merge_and_unload()
merged_model.push_to_hub("username/hr-assistant-7b")
```

#### 7.5 Fine-tuning UI (Admin Panel)

```
┌─────────────────────────────────────────────────────────────────┐
│  Fine-tuning Dashboard                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Create New Training Job                                 │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Type:  [Embedding ▼]                                    │   │
│  │ Base Model: [multilingual-e5-base ▼]                    │   │
│  │ Training Data: [Upload CSV] or [Select from Documents]  │   │
│  │ Output Name: [custom-e5-hr________________]             │   │
│  │                                        [Start Training] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Training Jobs                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Job ID    │ Type      │ Status    │ Progress │ Actions   │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ job-001   │ Embedding │ Running   │ ████░░ 67% │ [Stop]  │ │
│  │ job-002   │ Classifier│ Completed │ ██████ 100%│ [Deploy]│ │
│  │ job-003   │ LLM LoRA  │ Queued    │ ░░░░░░ 0%  │ [Cancel]│ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Deployed Models                                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Model Name          │ Type      │ Status │ Actions       │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ custom-e5-hr        │ Embedding │ Active │ [Use] [Delete]│ │
│  │ intent-classifier-th│ Classifier│ Active │ [Use] [Delete]│ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.6 Integration with Platform

```yaml
# Project config - use fine-tuned models
project:
  name: "HR Project"
  
embeddings:
  model: "username/custom-e5-hr"  # Fine-tuned model
  
classifier:
  model: "username/intent-classifier-th"  # Route queries
  
llm:
  model: "username/hr-assistant-7b"  # Via Ollama
  # OR
  model: "gpt-4"  # Via LiteLLM
```

---

### 8. Admin & Monitoring

#### 8.1 Admin Panel
- [ ] User management (view, edit, suspend)
- [ ] Usage overview (all users)
- [ ] System health dashboard
- [ ] Cost tracking
- [ ] Fine-tuning job management ⭐ NEW
- [ ] Database connection management ⭐ NEW

#### 8.2 Monitoring (Prometheus)
- [ ] Request latency
- [ ] Token usage per user
- [ ] Error rates
- [ ] RAG retrieval quality
- [ ] SQL query performance ⭐ NEW
- [ ] Fine-tuning job status ⭐ NEW

#### 8.3 Logging
- [ ] Request/response logs
- [ ] Error logs
- [ ] Audit logs (for enterprise)
- [ ] SQL query logs (with masking) ⭐ NEW

---

## 📁 Project Structure (Updated)

```
rag-agent-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── projects.py
│   │   │   ├── documents.py
│   │   │   ├── agents.py
│   │   │   ├── admin.py
│   │   │   ├── database.py          # ⭐ NEW: DB connections API
│   │   │   └── finetune.py          # ⭐ NEW: Fine-tuning API
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── llm_client.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   ├── db_connection.py     # ⭐ NEW
│   │   │   └── finetune_job.py      # ⭐ NEW
│   │   │
│   │   ├── rag/
│   │   │   ├── embeddings.py
│   │   │   ├── chunking.py
│   │   │   ├── retriever.py
│   │   │   └── pipeline.py
│   │   │
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── engine.py
│   │   │   ├── tools/
│   │   │   │   ├── rag_search.py
│   │   │   │   ├── summarize.py
│   │   │   │   ├── sql_query.py     # ⭐ NEW
│   │   │   │   └── chart_gen.py     # ⭐ NEW
│   │   │   └── prebuilt/
│   │   │       ├── general.py
│   │   │       ├── hr.py
│   │   │       ├── legal.py
│   │   │       ├── finance.py
│   │   │       └── data_analyst.py  # ⭐ NEW
│   │   │
│   │   ├── text2sql/                # ⭐ NEW
│   │   │   ├── __init__.py
│   │   │   ├── schema.py            # Schema discovery
│   │   │   ├── generator.py         # SQL generation
│   │   │   ├── validator.py         # SQL validation
│   │   │   ├── executor.py          # Safe execution
│   │   │   └── visualizer.py        # Result visualization
│   │   │
│   │   ├── finetune/                # ⭐ NEW
│   │   │   ├── __init__.py
│   │   │   ├── embedding.py         # Embedding fine-tuning
│   │   │   ├── classifier.py        # Classifier fine-tuning
│   │   │   ├── llm_lora.py          # LLM LoRA fine-tuning
│   │   │   ├── data_prep.py         # Training data preparation
│   │   │   └── hub.py               # Hugging Face Hub integration
│   │   │
│   │   ├── services/
│   │   │   ├── usage.py
│   │   │   ├── limits.py
│   │   │   └── notifications.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   └── rate_limit.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── test_rag.py
│   │   ├── test_agents.py
│   │   ├── test_text2sql.py         # ⭐ NEW
│   │   └── test_finetune.py         # ⭐ NEW
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +page.svelte
│   │   │   ├── +layout.svelte
│   │   │   ├── login/
│   │   │   ├── projects/
│   │   │   ├── settings/
│   │   │   ├── database/            # ⭐ NEW: DB management UI
│   │   │   ├── finetune/            # ⭐ NEW: Fine-tuning UI
│   │   │   └── admin/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Chat/
│   │   │   │   ├── Sidebar/
│   │   │   │   ├── AgentSelector/
│   │   │   │   ├── DebugPanel/
│   │   │   │   ├── SQLResult/       # ⭐ NEW
│   │   │   │   ├── ChartView/       # ⭐ NEW
│   │   │   │   └── UsageDashboard/
│   │   │   ├── stores/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── project.ts
│   │   │   │   └── chat.ts
│   │   │   └── api/
│   │   │       └── client.ts
│   │   └── app.html
│   ├── static/
│   ├── svelte.config.js
│   └── package.json
│
├── configs/
│   ├── base.yaml
│   ├── agents/
│   │   ├── general.yaml
│   │   ├── hr.yaml
│   │   ├── legal.yaml
│   │   ├── finance.yaml
│   │   └── data_analyst.yaml        # ⭐ NEW
│   └── databases/                   # ⭐ NEW
│       └── example_schema.yaml
│
├── training/                        # ⭐ NEW: Fine-tuning scripts
│   ├── notebooks/
│   │   ├── finetune_embedding.ipynb
│   │   ├── finetune_classifier.ipynb
│   │   └── finetune_llm_lora.ipynb
│   ├── scripts/
│   │   ├── prepare_data.py
│   │   ├── train_embedding.py
│   │   ├── train_classifier.py
│   │   └── train_lora.py
│   └── data/
│       └── sample/
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── AGENTS.md
│   ├── TEXT2SQL.md                  # ⭐ NEW
│   └── FINETUNING.md                # ⭐ NEW
│
├── Makefile
├── README.md
└── .env.example
```

---

## 📅 Development Phases (Updated)

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic working app with authentication

- [ ] Setup project structure
- [ ] Setup Hetzner VPS + Coolify
- [ ] Setup GitHub Actions CI/CD
- [ ] FastAPI backend skeleton
- [ ] SvelteKit frontend skeleton
- [ ] User authentication (register/login)
- [ ] Basic chat UI (no RAG yet)
- [ ] LiteLLM integration (single model)
- [ ] Docker containerization

**Deliverable**: User can login and chat with AI

---

### Phase 2: RAG Core (Week 3-4)
**Goal**: Document upload and RAG working

- [ ] Document upload API
- [ ] PDF/DOCX text extraction
- [ ] Text chunking (recursive)
- [ ] ChromaDB integration
- [ ] Embedding generation
- [ ] Basic retrieval (dense search)
- [ ] Source citations in responses
- [ ] Document management UI

**Deliverable**: User can upload docs and ask questions

---

### Phase 3: Agent System (Week 5-6)
**Goal**: Multi-agent with tools

- [ ] Agent base class
- [ ] Agent configuration loader (YAML)
- [ ] Agent execution engine
- [ ] Basic tools (search, summarize)
- [ ] Pre-built agents (General, HR, Legal)
- [ ] Agent selector UI
- [ ] Agent thinking display
- [ ] Tool execution visualization

**Deliverable**: User can select agents for different tasks

---

### Phase 4: Project System (Week 7)
**Goal**: Multi-project with isolated data

- [ ] Project CRUD API
- [ ] Per-project document storage
- [ ] Per-project conversations
- [ ] Project settings UI
- [ ] Project switching in sidebar
- [ ] Project-scoped RAG queries

**Deliverable**: User can organize work into projects

---

### Phase 5: Text-to-SQL ⭐ NEW (Week 8)
**Goal**: Query databases with natural language

- [ ] Database connection management
- [ ] Schema discovery & caching
- [ ] SQL generation with LLM
- [ ] SQL validation & safety checks
- [ ] Query execution (read-only)
- [ ] Result formatting (table, chart)
- [ ] Data Analyst agent
- [ ] Database settings UI

**Deliverable**: User can query their database using natural language

---

### Phase 6: Fine-tuning Module ⭐ NEW (Week 9-10)
**Goal**: Train custom models

- [ ] Training data preparation tools
- [ ] Embedding fine-tuning script
- [ ] Classifier fine-tuning script
- [ ] LLM LoRA fine-tuning script
- [ ] Hugging Face Hub integration
- [ ] Fine-tuning job management API
- [ ] Fine-tuning dashboard UI
- [ ] Integration with platform (use custom models)

**Deliverable**: User can fine-tune and deploy custom models

---

### Phase 7: Polish & Production (Week 11-12)
**Goal**: Production-ready features

- [ ] Usage tracking service
- [ ] User limits & quotas
- [ ] Rate limiting
- [ ] Usage dashboard UI
- [ ] Admin panel (full)
- [ ] Debug panel
- [ ] Error handling & retry
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation

**Deliverable**: Ready for demo/production

---

### Phase 8: Advanced Features (Optional)
**Goal**: Impressive extras

- [ ] Hybrid search (Dense + BM25)
- [ ] Re-ranking
- [ ] Multi-model switching
- [ ] A/B model comparison
- [ ] Voice input (STT)
- [ ] Voice output (TTS)
- [ ] Team sharing
- [ ] Custom agent builder UI
- [ ] MongoDB support for Text-to-SQL
- [ ] Multimodal RAG (images, audio)

---

## 🎓 Skills Coverage (Updated)

| Job Requirement | Project Feature | Status |
|-----------------|-----------------|--------|
| **RAG Pipeline** | Document upload, embedding, retrieval | ✅ |
| **Agentic AI** | Multi-agent system, tools, reasoning | ✅ |
| **Fine-tuning LLMs** | Embedding, Classifier, LLM LoRA fine-tuning | ✅ NEW |
| **Hugging Face** | Transformers, PEFT, Hub | ✅ NEW |
| **Python Scientific** | NumPy, Pandas, Data processing | ✅ |
| **RESTful APIs** | Full REST API | ✅ |
| **MLOps** | Prometheus, W&B, model deployment | ✅ |
| **CI/CD** | GitHub Actions | ✅ |
| **Large-scale Data** | Document processing, SQL queries | ✅ |
| **Data Analysis** | Text-to-SQL, visualization | ✅ NEW |

### ครบทุก Requirements ของ Sciology ✅

---

## 💬 Interview Talking Points (Updated)

### Elevator Pitch
> "ผมสร้าง RAG Agent Platform ที่เป็น domain-agnostic template รองรับ multi-project แต่ละ project มี isolated knowledge base และสามารถต่อ database ลูกค้าได้โดยตรง ผ่าน Text-to-SQL ที่ query ด้วยภาษาธรรมชาติ มี pre-built agents สำหรับ HR, Legal, Finance, Data Analysis พร้อมใช้ ระบบรองรับ fine-tuning ทั้ง embeddings, classifiers และ LLM ด้วย LoRA เพื่อปรับให้เหมาะกับ domain เฉพาะ ใช้ Hugging Face ecosystem ทั้งหมด และมี CI/CD pipeline พร้อม monitoring"

### Technical Deep-Dives

**Q: Fine-tuning ทำอะไรได้บ้าง?**
> "ผมทำ 3 แบบครับ: 
> 1) Fine-tune embeddings ด้วย sentence-transformers เพื่อปรับปรุง retrieval สำหรับ domain เฉพาะ
> 2) Fine-tune classifier ด้วย BERT เพื่อ route queries ไปยัง agent ที่เหมาะสม
> 3) Fine-tune LLM ด้วย QLoRA บน Qwen/Llama เพื่อให้ตอบในสไตล์ที่ต้องการ ใช้ Hugging Face Transformers และ PEFT library ทั้งหมด push model ขึ้น Hub ได้เลย"

**Q: Text-to-SQL ทำงานยังไง?**
> "ผมส่ง schema context (ชื่อตาราง, คอลัมน์, relationships) ให้ LLM พร้อม query ภาษาธรรมชาติ LLM generate SQL แล้วผ่าน validator ที่ check ว่าเป็น SELECT only, ไม่มี destructive operations จากนั้น execute ใน sandbox ที่มี timeout และ row limit แสดงผลเป็น table หรือ auto-generate chart"

**Q: RAG ทำงานยังไง?**
> "ใช้ hybrid search รวม dense embeddings (multilingual-e5 หรือ fine-tuned) กับ BM25 แล้ว fuse ด้วย Reciprocal Rank Fusion สามารถใช้ fine-tuned embeddings ที่ train บน domain data ได้ ทำให้ retrieval accuracy สูงขึ้น"

**Q: Production-ready ไหม?**
> "มี error handling ครบ, retry logic, rate limiting ผ่าน LiteLLM, monitoring ด้วย Prometheus, experiment tracking ด้วย W&B, CI/CD ที่ test ก่อน deploy และมี security features สำหรับ Text-to-SQL เช่น read-only mode, query validation, sensitive data masking"

---

## 📎 Appendix

### A. Environment Variables (Updated)

```env
# App
APP_NAME=RAG Agent Platform
APP_ENV=production
SECRET_KEY=your-secret-key

# Database (Internal)
DATABASE_URL=postgresql://user:pass@localhost:5432/ragagent

# LiteLLM
LITELLM_MASTER_KEY=sk-master-key
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx

# Embeddings
EMBEDDING_MODEL=intfloat/multilingual-e5-base
# Or fine-tuned: username/custom-e5-hr

# Hugging Face
HF_TOKEN=hf_xxx
HF_USERNAME=your-username

# Weights & Biases (optional)
WANDB_API_KEY=xxx

# Storage
UPLOAD_DIR=/data/uploads
CHROMA_DIR=/data/chroma
MODELS_DIR=/data/models

# Text-to-SQL
SQL_QUERY_TIMEOUT=30
SQL_MAX_ROWS=1000
```

### B. API Endpoints (Updated)

```
Auth
  POST   /api/auth/register
  POST   /api/auth/login
  POST   /api/auth/logout
  GET    /api/auth/me

Projects
  GET    /api/projects
  POST   /api/projects
  GET    /api/projects/{id}
  PUT    /api/projects/{id}
  DELETE /api/projects/{id}

Documents
  GET    /api/projects/{id}/documents
  POST   /api/projects/{id}/documents
  DELETE /api/projects/{id}/documents/{doc_id}

Chat
  POST   /api/projects/{id}/chat
  GET    /api/projects/{id}/conversations
  GET    /api/projects/{id}/conversations/{conv_id}

Agents
  GET    /api/agents
  GET    /api/agents/{id}

Database Connections (NEW)
  GET    /api/projects/{id}/databases
  POST   /api/projects/{id}/databases
  GET    /api/projects/{id}/databases/{db_id}/schema
  POST   /api/projects/{id}/databases/{db_id}/test
  DELETE /api/projects/{id}/databases/{db_id}
  POST   /api/projects/{id}/databases/{db_id}/query

Fine-tuning (NEW)
  GET    /api/finetune/jobs
  POST   /api/finetune/jobs
  GET    /api/finetune/jobs/{job_id}
  POST   /api/finetune/jobs/{job_id}/stop
  GET    /api/finetune/models
  POST   /api/finetune/models/{model_id}/deploy
  DELETE /api/finetune/models/{model_id}

Admin
  GET    /api/admin/users
  PUT    /api/admin/users/{id}
  GET    /api/admin/usage
  GET    /api/admin/finetune/jobs
```

### C. Docker Compose (Updated)

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ragagent
      - LITELLM_URL=http://litellm:4000
      - HF_TOKEN=${HF_TOKEN}
    depends_on:
      - db
      - litellm
    volumes:
      - ./data:/data
      - ./models:/models

  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - UI_USERNAME=admin
      - UI_PASSWORD=${LITELLM_UI_PASSWORD}
    volumes:
      - ./litellm-config.yaml:/app/config.yaml

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=ragagent
    volumes:
      - postgres_data:/var/lib/postgresql/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  # Optional: Ollama for local fine-tuned models
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # If GPU available

volumes:
  postgres_data:
  ollama_data:
```

### D. Training Requirements (NEW)

```txt
# training/requirements.txt
torch>=2.0.0
transformers>=4.36.0
sentence-transformers>=2.2.0
datasets>=2.16.0
peft>=0.7.0
trl>=0.7.0
bitsandbytes>=0.41.0
accelerate>=0.25.0
wandb>=0.16.0
huggingface_hub>=0.20.0
scikit-learn>=1.3.0
```

---

## ✅ Ready to Start

- [ ] Create GitHub repository
- [ ] Setup Hetzner VPS
- [ ] Install Coolify
- [ ] Configure GitHub Actions
- [ ] Create Hugging Face account & token
- [ ] Begin Phase 1

---

## 📊 Timeline Summary

| Phase | Week | Features |
|-------|------|----------|
| 1. Foundation | 1-2 | Auth, Chat, LiteLLM |
| 2. RAG Core | 3-4 | Documents, Embeddings, Retrieval |
| 3. Agent System | 5-6 | Multi-agent, Tools |
| 4. Project System | 7 | Multi-project, Isolation |
| 5. Text-to-SQL | 8 | Database queries ⭐ |
| 6. Fine-tuning | 9-10 | Custom models ⭐ |
| 7. Polish | 11-12 | Production-ready |

**Total: 12 weeks (3 months)**

---

*Document Version 2.0 - December 2024*
*Added: Fine-tuning Module, Text-to-SQL System*