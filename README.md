
# 🚀 Hindsight-Powered AI Group Project Manager

**The project manager that never forgets, ensuring your team never repeats the same mistake twice.**

[](https://hindsight-manager-blrtuzwxruorhqoskhpmmf.streamlit.app/)

## 📝 The Problem: "Collective Amnesia"

Most student and startup teams suffer from "Collective Amnesia". Decisions made in week 1 are forgotten by week 4, and tasks are often assigned to the wrong people because standard AI chatbots are stateless—they have no long-term memory of a team's history or individual expertise.

## 💡 The Solution: A Stateful AI Orchestrator

We built a memory-driven manager that uses **Hindsight’s Vectorized Memory** to remember every team decision and expert specialty. It doesn't just chat; it manages based on evolving experience.

### 🌟 Key Features

  * **Expertise-Aware Tasking**: The AI identifies that **Rahul** is the Frontend Lead and **Dexter** is the Backend Architect, assigning work based on proven capability.
  * **Stateful Retrospectives**: Uses a memory loop to recall *why* a decision was made weeks ago.
  * **Dynamic Onboarding**: A custom flow to define project scopes and team roles instantly.
  * **Premium UI**: A sleek, Anthropic-inspired interface designed for clarity and focus.

-----

## 🛠️ Technical Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Brain** | **Groq (Qwen-3 32B)** | Instant, sub-second inference for real-time logic. |
| **Memory** | **Hindsight Cloud** | Persistent vector storage for a "long-term brain". |
| **Interface** | **Streamlit** | A responsive, custom-styled web application. |
| **Execution** | **Async Python** | Handles complex memory loops without freezing the UI. |

-----

## 🧠 Hindsight Integration: The "Memory Loop"

Unlike standard, stateless RAG systems, we use Hindsight to create a robust **"Memory Loop"** that retains and recalls organic team context.

### 📐 Project Architecture

The diagram below illustrates how we transition from "Existing Agent Systems" (Stateless) to "Vectorize-Powered Agentic Memory" (Stateful) using **Contextualization**, **RAG Operations**, and **Memory Management**(./Architecture.jpeg)

### 💻 Implementation Example

Below is the core logic of how we securely store project experiences within this loop, enabling the AI to gain experience with every interaction.

```python
# Standard "Stateless" AI would forget this after one session.
# We use Hindsight to make it permanent.
await hindsight.retain(
    "Team Decision", 
    content=f"{member_name} assigned to {task_name} due to {expertise} expertise",
    metadata={"project": project_name}
)
```

-----

## 🚀 Installation & Setup

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/Sohan4-c/hindsight-manager.git
    cd hindsight-manager
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables**:
    Create a `.env` file with your keys:
    ```text
    GROQ_API_KEY=your_key_here
    HINDSIGHT_API_KEY=your_key_here
    ```
4.  **Run Locally**:
    ```bash
    streamlit run app.py
    ```

-----

## 👥 The Team

  * **Dexter**: AI Architect & Backend Lead.
  * **Rahul**: Lead Frontend Engineer.
  * **Sohan**: Project Coordinator & System Design.

-----

## 🔗 Links

  * **Live Demo**: [Hindsight Manager App](https://hindsight-manager-blrtuzwxruorhqoskhpmmf.streamlit.app/).
  * **Built with**: [Hindsight Open Source Agent Memory](https://github.com/vectorize-io/hindsight).

-----
