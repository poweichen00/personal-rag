# 個人 RAG

> 本地優先、附出處引用的 RAG 範本。把你自己的文件放進 `data/raw/`，就得到一個只根據你的文件作答、並標註出處的私人助理，不需雲端、也不需 API 金鑰。內建 22 篇範例語料，clone 下來即可直接執行。

[![CI](https://github.com/poweichen00/personal-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/poweichen00/personal-rag/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Embeddings](https://img.shields.io/badge/Embeddings-Ollama%20nomic--embed--text-000000?logo=ollama&logoColor=white)
![Vector DB](https://img.shields.io/badge/Vector%20DB-ChromaDB-FF6B6B)
![Architecture](https://img.shields.io/badge/Architecture-RAG-4B8BBE)
![Local-First](https://img.shields.io/badge/Local--First-No%20Docker-success)

[English](README.md) | **繁體中文**

<p align="center">
  <img src="assets/demo.svg" alt="帶行內出處的回答，在 Jetson Orin 上完全離線生成" width="820">
  <br>
  <em>在 Jetson Orin 上完全離線回答一個自然語言問題，每個論點都標註了來源。</em>
</p>

---

## 專案簡介

把它指向一個裝著你自己文件的資料夾（論文、筆記、內部文件、PDF），它就成為你個人的檢索增強（RAG）助理：用自然語言提問，它便**只根據你的文件**作答，並在行內標註每個出處，讓每個論點都可被驗證。

整套系統跑在本地、免費的模型上（Ollama + ChromaDB），生成階段使用 OpenAI 相容的端點，所以資料不會離開你的機器，也不需要 API 金鑰。

repo 內建一份 22 篇無人機小物體偵測的語料，作為可直接執行的範例。換成你自己的檔案，它就成為你專屬的助理（見下方「換成你自己的資料」）。

## 特色

- **附出處的回答**：每則回答都引用來源文件與區塊，論點可被驗證。
- **本地優先且免費**：Ollama 嵌入 + ChromaDB + 可選的本地 Ollama 生成；**不需要 OpenAI 帳號、免 Docker、零雲端成本**。
- **冪等且增量的索引**：MD5 雜湊快取 + 確定性 upsert，重跑安全又快速。
- **混合檢索**：稠密 cosine 相似度結合詞彙重疊重排，結果更精準。
- **自動產生 skill 規格**：產出結構化的 `skill.md`；即使沒有 LLM，也會以確定性的方式生成。
- **互動或單次查詢**：支援多輪 REPL 或一次性的 `--query` 模式。

---

## 快速開始

完全本地、不需要 API 金鑰。需要 Python 3.10+ 與 [Ollama](https://ollama.ai)。

```bash
git clone https://github.com/poweichen00/personal-rag.git && cd personal-rag
pip install -r requirements.txt

ollama serve &                                         # 啟動 Ollama（localhost:11434）
ollama pull nomic-embed-text && ollama pull llama3.1   # 嵌入 + LLM
cp .env.example .env                                   # 預設已指向本地 Ollama

python3 src/data_update.py --rebuild                       # 建立向量索引
python3 src/rag_query.py                                   # 互動式提問
```

想改用雲端 LLM（OpenAI、vLLM、LM Studio 等）？改 `.env` 裡的 `LITELLM_*` 與 `DEFAULT_LLM_MODEL` 幾行就好，其餘不變。

---

## 使用方式

```bash
python3 src/data_update.py                 # 增量重建索引（只處理變動的檔案）
python3 src/rag_query.py --query "..."     # 單次提問
python3 src/rag_query.py --help            # 所有參數（--top-k、--model 等）
python3 src/skill_builder.py               # 從知識庫產生 skill.md
```

---

## 範例

上方 demo 的純文字版（方便複製；內建 22 篇語料，以 `qwen2.5:7b` + `nomic-embed-text` 完全離線生成）：

<details>
<summary>以文字顯示這次執行</summary>

```console
$ python3 src/rag_query.py --query "Why does IoU-based label assignment perform poorly for tiny objects?"

[INFO] Embedding query ...
[INFO] Retrieving top-5 chunks ...
[INFO] Generating answer ...

[Assistant] IoU-based (Intersection over Union) label assignment performs poorly for
tiny objects because of several fundamental issues:

1. Zero IoU for non-overlapping predictions: a predicted box 2 pixels from a 5x5
   ground-truth box has IoU = 0 despite being geometrically close, so training gets
   no gradient signal.  [Source: paper_03_nwd_wasserstein.md, chunk 5/8]

2. High sensitivity to small displacements: translating a 4x4 box by even a single
   pixel can drop IoU from 1.0 to 0.0.  [Source: paper_02_rfla_label_assignment.md, chunk 4/9]

3. IoU ignores scale context: two 4x4 boxes 3 pixels apart should be scored
   differently from two 400x400 boxes the same distance apart, but IoU treats them
   identically.  [Source: paper_03_nwd_wasserstein.md, chunk 5/8]

── Sources ──────────────────────────────────────
  [1] paper_02_rfla_label_assignment.md  chunk 2/9  (similarity=0.7241)
  [2] paper_02_rfla_label_assignment.md  chunk 4/9  (similarity=0.7163)
  [3] paper_11_atss.md  chunk 8/8  (similarity=0.6872)
  [4] paper_12_fcos.md  chunk 5/7  (similarity=0.6328)
  [5] paper_03_nwd_wasserstein.md  chunk 5/8  (similarity=0.6237)
─────────────────────────────────────────────────
```

</details>

> 答案為節錄。模型只根據檢索到的段落作答並逐一標註出處，因此每個論點都可被驗證。

---

## 運作方式

**索引建立**：`data/raw/` 裡的文件會先清理，切成段落感知的區塊（600 字元、重疊 100），用 Ollama `nomic-embed-text`（768 維）嵌入後存進 ChromaDB。

**查詢**：你的問題會先轉成向量，用 cosine 相似度取出候選區塊（先多取 K 的 3 倍），再以混合分數（0.7 cosine + 0.3 詞彙重疊）重排，最後把最相關的前 K 個交給 OpenAI 相容的 LLM，生成帶行內出處的回答。

---

## 換成你自己的資料

內建語料是無人機小物體偵測的範例，但整條管線是通用的。先確認上面「快速開始」與「使用方式」在內建範例上能正常執行，再依下面 4 步換成你自己的資料，**完全不用改程式碼**。

### Step 1: 放入你的文件

把 `data/raw/` 裡內建的 22 篇論文換成你自己的檔案（支援 Markdown、純文字、PDF；摘要與結構化筆記的索引效果通常優於 500 頁的長 PDF）。

```bash
git clone https://github.com/poweichen00/personal-rag.git
cd personal-rag

# 建議:先移除內建 UAV 範例,做乾淨切換
rm data/raw/paper_*.md

# 把你自己的檔案複製進去
cp ~/your-docs/*.md  data/raw/      # 或 *.pdf、*.txt
```

> 保留內建論文、與你的資料並存，技術上可行，但**不同主題混在同一個向量庫通常會傷害檢索品質**。除非你刻意要混用，否則建議先移除內建範例，再放入自己的檔案。

### Step 2: 告訴系統你的領域

編輯 `.env`（沒有就先 `cp .env.example .env`），設兩個變數。實際範例：

```bash
RAG_DOMAIN=quantum computing fundamentals
COLLECTION_NAME=quantum_computing
```

`RAG_DOMAIN` 會寫進助理的 system prompt；`COLLECTION_NAME` 讓你的新向量庫與內建的 UAV 向量庫分開存放。

### Step 3:（可選）自訂種子問題

`skill_builder.py` 會用幾個種子問題探測知識庫。要覆蓋內建（UAV）預設，建立一份 JSON：

```json
{
  "concepts": ["What is X?", "How does Y work?"],
  "trends":   ["How has Z evolved over time?"],
  "entities": ["Which datasets / methods / people are central?"]
}
```

然後在 `.env` 加上：

```bash
SEED_QUESTIONS_FILE=./seed_questions.json
```

### Step 4: 重建索引並查詢

```bash
python3 src/data_update.py --rebuild
python3 src/rag_query.py --query "你的問題"
```

檢索、重排與其餘整條管線都會原封不動地套用在你的資料上。

---

## 測試

文字處理與檢索的輔助函式都有單元測試。測試直接針對純函式，所以**不需要 Ollama 或 ChromaDB**：

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## 技術選型

| 元件 | 技術 | 原因 |
|-----------|-----------|-----|
| 嵌入 | Ollama `nomic-embed-text` | 免費、本地、768 維 |
| 向量資料庫 | ChromaDB（PersistentClient） | 純 Python、免 Docker |
| LLM | 任何 OpenAI 相容端點，本地（Ollama、LM Studio）或雲端 | 可插拔；透過 `.env` 切換模型 |
| PDF 解析 | pypdf | 輕量、純 Python |
| 環境管理 | python-dotenv | 讓金鑰不進入程式碼 |

---

## 專案結構

```
.
├── src/
│   ├── data_update.py     # 管線：raw → 清理 → 切塊 → 嵌入 → ChromaDB
│   ├── rag_query.py       # 查詢介面：嵌入 → 檢索 → 重排 → LLM → 回答
│   └── skill_builder.py   # 從 RAG 知識庫產生 skill.md
├── tests/                 # 切塊與檢索的單元測試（pytest）
├── data/
│   ├── raw/               # 22 篇 Markdown 格式的來源論文
│   └── processed/         # 清理後的純文字（自動產生，已加入 git-ignore）
├── chroma_db/             # ChromaDB 持久化向量資料庫（已加入 git-ignore）
├── skill.md               # 結構化的 agent skill 描述（自動產生，已加入 git-ignore）
├── requirements.txt       # Python 相依套件
├── requirements-dev.txt   # 開發／測試相依套件（pytest）
├── .env.example           # 環境變數範本（不含真實金鑰）
└── .gitignore
```

---

## 內建範例

> 這一段描述的是**內建的 UAV 範例**。換成你自己的資料（見上方「換成你自己的資料」）後，這裡會改為反映你所索引的內容。

**主題：** 無人機小物體偵測（UAV Small Object Detection）。這份 22 篇語料涵蓋：

- **資料集**：VisDrone、DOTA
- **標籤指派（Label Assignment）**：ATSS、RFLA、NWD
- **Anchor-free 偵測器**：FCOS、CenterNet、TOOD
- **Transformer 系列**：Deformable DETR、DINO、QueryDet
- **注意力與骨幹網路**：CBAM、FPN、LSKNet、PKINet
- **推論技巧**：SAHI（切片輔助超推論）
- **輕量化模型**：SlimNet、GSConv、YOLOv9、LAM-YOLO
- **超解析度**：B2BDet

所有論文皆為 arXiv 上採開放授權的著作；`data/raw/` 中每個檔案的檔頭都記載了標題、arXiv ID、作者、發表會議與授權。其中 20 篇為 **CC BY 4.0**，SAHI 的參考實作以 **Apache 2.0** 釋出，另有兩篇含非商業／禁止改作條款（**FCOS** CC BY-NC-SA 4.0、**QueryDet** CC BY-NC-ND 4.0）。本語料僅用於非商業之研究與學習並完整標註出處，原作者保留一切權利。

<details>
<summary><b>完整論文清單（22 篇，點擊展開）</b></summary>

| # | 標題（簡稱） | 會議 / 年份 | arXiv | 授權 |
|--:|---------------|--------------|-------|---------|
| 01 | Vision Meets Drones (VisDrone) | arXiv 2018 | [1804.07437](https://arxiv.org/abs/1804.07437) | CC BY 4.0 |
| 02 | RFLA: Gaussian Receptive Field Label Assignment | ECCV 2022 | [2208.08738](https://arxiv.org/abs/2208.08738) | CC BY 4.0 |
| 03 | Normalized Gaussian Wasserstein Distance (NWD) | ISPRS J. 2022 | [2110.13389](https://arxiv.org/abs/2110.13389) | CC BY 4.0 |
| 04 | Slicing Aided Hyper Inference (SAHI) | ICIP 2022 | [2202.06934](https://arxiv.org/abs/2202.06934) | Apache 2.0 |
| 05 | TPH-YOLOv5 (Transformer Prediction Head) | ICCV-W 2021 | [2108.11539](https://arxiv.org/abs/2108.11539) | CC BY 4.0 |
| 06 | DOTA: Large-Scale Aerial Detection Dataset | CVPR 2018 | [1711.10398](https://arxiv.org/abs/1711.10398) | CC BY 4.0 |
| 07 | PKINet: Poly Kernel Inception Network | CVPR 2024 | [2403.06258](https://arxiv.org/abs/2403.06258) | CC BY 4.0 |
| 08 | Slim-Neck by GSConv | arXiv 2022 | [2206.02424](https://arxiv.org/abs/2206.02424) | CC BY 4.0 |
| 09 | Deformable DETR | ICLR 2021 | [2010.04159](https://arxiv.org/abs/2010.04159) | CC BY 4.0 |
| 10 | LSKNet: Large Selective Kernel Network | ICCV 2023 | [2303.09030](https://arxiv.org/abs/2303.09030) | CC BY 4.0 |
| 11 | ATSS: Adaptive Training Sample Selection | CVPR 2020 | [1912.02424](https://arxiv.org/abs/1912.02424) | CC BY 4.0 |
| 12 | FCOS: Fully Convolutional One-Stage | ICCV 2019 | [1904.01355](https://arxiv.org/abs/1904.01355) | CC BY-NC-SA 4.0 |
| 13 | TOOD: Task-Aligned One-Stage Detection | ICCV 2021 | [2108.07755](https://arxiv.org/abs/2108.07755) | CC BY 4.0 |
| 14 | QueryDet: Cascaded Sparse Query | CVPR 2022 | [2103.09136](https://arxiv.org/abs/2103.09136) | CC BY-NC-ND 4.0 |
| 15 | DINO: DETR with Improved DeNoising | arXiv 2022 | [2203.03605](https://arxiv.org/abs/2203.03605) | CC BY 4.0 |
| 16 | CBAM: Convolutional Block Attention Module | ECCV 2018 | [1807.06521](https://arxiv.org/abs/1807.06521) | CC BY 4.0 |
| 17 | FPN: Feature Pyramid Networks | CVPR 2017 | [1612.03144](https://arxiv.org/abs/1612.03144) | CC BY 4.0 |
| 18 | CenterNet: Objects as Points | arXiv 2019 | [1904.07850](https://arxiv.org/abs/1904.07850) | CC BY 4.0 |
| 19 | YOLOv9: Programmable Gradient Information | arXiv 2024 | [2402.13616](https://arxiv.org/abs/2402.13616) | CC BY 4.0 |
| 20 | LAM-YOLO: Lighting-Occlusion Attention YOLO | arXiv 2024 | [2411.00485](https://arxiv.org/abs/2411.00485) | CC BY 4.0 |
| 21 | Scale Optimization via Evolutionary RL | AAAI 2024 | [2312.15219](https://arxiv.org/abs/2312.15219) | CC BY 4.0 |
| 22 | B2BDet: Aerial Detection with Super-Resolution | arXiv 2024 | [2401.14661](https://arxiv.org/abs/2401.14661) | CC BY 4.0 |

</details>

---

## 專案統計

| 指標 | 數值 |
|---|---|
| 來源論文 | 22 篇（arXiv，2016-2025） |
| 語料 | 約 11,300 個英文單字（摘要與結構化筆記） |
| 向量區塊 | 183 塊（每篇平均 8.3，範圍 7-11） |
| 區塊長度 | 平均 453 字元，中位數 483（上限 600，重疊 100） |
| 嵌入維度 | 768（nomic-embed-text） |
| 主題分類 | 8 大類（資料集、標籤指派、anchor-free、Transformer、注意力、推論技巧、輕量化、超解析度） |
| 相似度指標 | Cosine + 詞彙重疊重排 |
| Top-K 檢索 | 每次 5 塊（先取 K×3 再重排） |

---

## 授權與出處

- **專案程式碼** 以 [MIT License](LICENSE) 釋出。
- **來源論文** 保留其原始授權（見 [內建範例](#內建範例)），在此僅用於非商業研究並標註出處。

---

## 致謝

本專案建立於無人機／小物體偵測社群的開放研究之上，感謝 VisDrone、DOTA、NWD、RFLA、SAHI 及上方所列各論文的作者。技術支援：[Ollama](https://ollama.ai)、[ChromaDB](https://www.trychroma.com/) 與 [nomic-embed-text](https://www.nomic.ai/) 嵌入模型。
