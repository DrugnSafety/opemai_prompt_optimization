# 🚀 GPT-4.1 Prompt Optimizer

**Human-in-the-Loop Prompt Optimization System**

An advanced prompt optimization tool based on OpenAI's [Prompt Optimization Cookbook](https://cookbook.openai.com/examples/optimize_prompts), enabling iterative improvement through user feedback.

> **📖 Reference**: This project is developed based on [OpenAI Cookbook's Prompt Optimization example](https://cookbook.openai.com/examples/optimize_prompts) and provides extended functionality by integrating GPT-4.1 guidelines.

## 👨‍💻 Developer Information

**Mingyu Kang**
- 📧 **Email**: [irreversibly@gmail.com](mailto:irreversibly@gmail.com)
- 💼 **LinkedIn**: [linkedin.com/in/mingyu-kang-28473493](https://linkedin.com/in/mingyu-kang-28473493)
- 🏠 **Homepage**: [https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63](https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63)

## ✨ Key Features

### 🔍 **Automated Prompt Analysis - Checker System**

This tool performs comprehensive prompt analysis through 4 specialized checkers:

#### 1. **Clarity Checker**
- **Function**: Analyzes prompt clarity and comprehensibility
- **Check Items**:
  - Detection of ambiguous expressions (maybe, perhaps, might, etc.)
  - Role definition clarity assessment
  - Excessive question inclusion check
  - Prompt length appropriateness evaluation
- **Output**: List of clarity-related issues and severity assessment

#### 2. **Specificity Checker**
- **Function**: Evaluates specificity and detail of instructions
- **Check Items**:
  - Detection of abstract instructions (do something, help me, etc.)
  - Output format specification verification
  - Prompt context sufficiency evaluation
  - Planning guidance presence for tool usage
- **Output**: Identification of areas needing specificity improvement

#### 3. **Instruction Following Checker**
- **Function**: Verifies consistency and executability of instructions
- **Check Items**:
  - Detection of conflicting instructions (always vs never, must vs optional)
  - Sentence completeness check
  - Priority clarity evaluation
  - Instruction structuring degree analysis
- **Output**: Identification of contradictions and instructions needing improvement

#### 4. **Agentic Capability Checker**
- **Function**: Optimization analysis for GPT-4.1's agentic workflow capabilities
- **Check Items**:
  - Planning capability induction assessment
  - Reflective thinking process inclusion
  - Step-by-step approach specification
  - Tool usage and external resource utilization guidelines
  - Task persistence and state management considerations
- **Output**: Improvement suggestions for enhancing agentic functionality

### 🛠️ **Automated Optimization System**

#### Prompt Optimizer Agent
- **Function**: Automatically improves prompts based on analysis results
- **Process**:
  1. Integrated analysis of all Checker results
  2. Generation of improvement plans based on GPT-4.1 guidelines
  3. Structured prompt rewriting
  4. Expected performance improvement rate calculation

#### Few-shot Optimizer Agent
- **Function**: Improves consistency and effectiveness of few-shot examples
- **Process**:
  - Consistency check between examples and prompt
  - Example quality evaluation and improvement
  - Optimal example count and structure suggestion

### 💬 **Human-in-the-Loop Improvement System**

#### Feedback Analyzer Agent
- **Function**: Structures and analyzes user feedback
- **Process**:
  - Automatic feedback category classification
  - Improvement priority determination
  - Modification strategy establishment

#### Prompt Reviser Agent
- **Function**: Additional prompt improvement based on feedback
- **Process**:
  - Feedback reflection planning
  - Gradual prompt modification
  - Change tracking and documentation

### 🎨 **User-Friendly Interface**
- Streamlit-based web interface
- 5-stage tab structure (Input → Analysis → Results → Optimization → Feedback)
- Real-time progress display
- Result download and sharing functionality
- Multi-language support (Korean/English)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prompt Input   │───▶│ Auto Analysis    │───▶│ Optimization     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Few-shot       │    │  Parallel       │    │ Feedback Input   │
│  Examples       │    │  Checkers       │    └─────────────────┘
└─────────────────┘    └─────────────────┘              │
                                │                       ▼
                                ▼              ┌─────────────────┐
                       ┌─────────────────┐    │ Feedback        │
                       │ Issue Detection  │    │ Analysis        │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Auto Correction  │    │ Additional      │
                       └─────────────────┘    │ Improvement     │
                                              └─────────────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd openai_prompt_optimization

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. Execution

#### Web Interface (Recommended)
```bash
streamlit run app.py
```
Access `http://localhost:8501` in browser

#### Command Line Test
```bash
python test_optimizer.py
```

## 📋 Usage

### 1. Prompt Input
- Write main prompt
- Add few-shot examples (optional)
- Configure advanced settings

### 2. Automated Analysis
- 4 specialized agents analyze in parallel
- Check real-time progress
- Review discovered issues

### 3. Optimization Results
- Review improved prompt
- Check applied changes
- Compare before/after

### 4. Feedback-based Improvement
- Provide feedback on optimized prompt
- Request additional improvements
- Perform iterative enhancement

## 🔧 Technology Stack

### Backend
- **Python 3.13**: Latest Python version utilization
- **FastAPI**: Asynchronous web framework
- **Pydantic**: Data validation and serialization
- **asyncio**: Asynchronous processing
- **OpenAI API**: GPT-4.1 model utilization

### Frontend
- **Streamlit**: Interactive web application
- **Tailwind CSS**: Modern UI design
- **JavaScript**: Dynamic interactions

### Development Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework

## 📊 Differences from OpenAI Cookbook

### 🔄 **Key Improvements**

#### 1. **Dependency Issue Resolution**
```python
# Original (dependency conflicts)
from agents import Agent, Runner, set_default_openai_client, trace

# Improved version (self-implemented)
class Agent:
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    @staticmethod
    async def run(agent: Agent, input_data: str, progress_callback=None):
        # Self-implemented agent execution logic
```

#### 2. **GPT-4.1 Guidelines Integration**
```python
# New agent types added
clarity_checker = Agent(
    name="clarity_checker",
    model="gpt-4.1",
    output_type=Issues,
    instructions="Clarity analysis..."
)

specificity_checker = Agent(
    name="specificity_checker", 
    model="gpt-4.1",
    output_type=Issues,
    instructions="Specificity analysis..."
)

instruction_following_checker = Agent(
    name="instruction_following_checker",
    model="gpt-4.1", 
    output_type=Issues,
    instructions="Instruction following analysis..."
)

agentic_capability_checker = Agent(
    name="agentic_capability_checker",
    model="gpt-4.1",
    output_type=Issues, 
    instructions="Agentic capability analysis..."
)
```

#### 3. **Human-in-the-Loop System**
```python
# Feedback analysis and improvement
async def revise_prompt_with_feedback(
    optimized_prompt: str,
    user_feedback: str,
    progress_callback=None
) -> Dict[str, Any]:
    """Additional improvement of optimized prompt based on feedback"""
    
    # Step 1: Feedback analysis
    feedback_analysis_result = await Runner.run(
        feedback_analyzer,
        json.dumps({"user_feedback": user_feedback}),
        progress_callback
    )
    
    # Step 2: Prompt modification
    revision_result = await Runner.run(
        prompt_reviser,
        json.dumps({
            "original_optimized_prompt": optimized_prompt,
            "user_feedback": user_feedback
        }),
        progress_callback
    )
    
    return {
        "original_optimized_prompt": optimized_prompt,
        "user_feedback": user_feedback,
        "feedback_analysis": feedback_analysis_result.final_output.model_dump(),
        "revision_details": revision_result.final_output.model_dump(),
        "revised_prompt": revision_result.final_output.revised_prompt,
        "changes_made": revision_result.final_output.changes_made,
        "feedback_addressed": revision_result.final_output.feedback_addressed
    }
```

#### 4. **Web Interface Addition**
```python
# Streamlit-based user interface
import streamlit as st

# 5-stage tab structure
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Prompt Input", 
    "🔍 Analysis Progress", 
    "📊 Analysis Results", 
    "✨ Optimization Results",
    "🔄 Feedback & Revision"
])
```

## 🧪 Testing

### Automated Testing
```bash
# Run all tests
python test_optimizer.py

# Individual tests
python -m pytest tests/
```

### Test Scenarios
1. **Basic prompt optimization**
2. **Optimization with few-shot examples**
3. **Feedback-based additional improvement**
4. **Error handling and exception cases**

## 📝 License

MIT License - Free to use, modify, and distribute

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support & Contact

- **Developer Email**: [irreversibly@gmail.com](mailto:irreversibly@gmail.com)
- **LinkedIn**: [mingyu-kang-28473493](https://linkedin.com/in/mingyu-kang-28473493)
- **Developer Blog**: [https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63](https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63)

## 🙏 Acknowledgments

- **[OpenAI Cookbook](https://cookbook.openai.com/examples/optimize_prompts)** team - Providing excellent examples that became the foundation of this project
- **[GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)** - Latest prompting technique guidelines
- **Streamlit development team** - User-friendly web interface framework
- **OpenAI** - Powerful AI models and API provision
- All open source contributors

## 📚 Additional Resources

- **Referenced OpenAI Cookbook example**: [https://cookbook.openai.com/examples/optimize_prompts](https://cookbook.openai.com/examples/optimize_prompts)
- **GPT-4.1 Official Guide**: [https://cookbook.openai.com/examples/gpt4-1_prompting_guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)
- **Developer Portfolio**: [https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63](https://secretive-feels-f92.notion.site/1b502c77e2c980158dcef59faefeae63)

---

**Made with ❤️ by Mingyu Kang - For better AI prompts and Human-AI collaboration** 