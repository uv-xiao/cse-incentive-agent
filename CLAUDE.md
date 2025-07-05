# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Civil Service Exam Study Agent (考公Agent) designed to support ZZW in their civil service exam preparation journey. The system provides daily questionnaires, generates encouraging summary reports, and maintains a points-based reward/punishment system to gamify the study process.

## Development Commands

This project uses pixi for Python environment management. Common commands include:

```bash
# Initialize pixi project (once)
pixi init

# Add Python and dependencies
pixi add python
pixi add pandas matplotlib # Add other dependencies as needed

# Run the main application
pixi run python main.py

# Install all dependencies from pixi.toml
pixi install

# Run commands in pixi environment
pixi shell  # Activate pixi environment
```

## Architecture & Core Components

The system consists of four main functional modules, all of which have been implemented:

### 1. Daily Questionnaire Module (`modules/questionnaire.py`)
- Generates comprehensive daily questionnaires with 14 questions
- Multiple-choice format for easy filling
- Covers: study duration, practice problems, emotional state, physical condition, sleep quality, diet, breaks, review tasks, note-taking
- Auto-fills date and validates responses

### 2. Scoring System (`modules/scoring.py`)
- Implements detailed scoring rules based on `resources/red_black_list.jpg`
- Point categories:
  - Daily check-in: +2 points
  - Study duration: +2 to +10 points (30min to 180min+)
  - Practice problems: +2 to +10 points (10 to 50+ problems)
  - Healthy habits: +1 to +2 points (sleep, diet, breaks)
  - Review and notes: +2 to +4 points
  - Perfect streaks: +10 (weekly), +50 (monthly)
  - Penalties: -1 to -2 points (no study, poor sleep, anxiety, etc.)
- Level system with 6 tiers (初学者 to 考神)
- Personalized encouragement messages

### 3. Report Generator (`modules/report_generator.py`)
- Integrates with gemini-cli for AI-powered report generation
- Creates markdown/PDF reports with:
  - Daily performance analysis
  - Points breakdown with explanations
  - Trend analysis (comparing with historical data)
  - Personalized encouragement and suggestions
  - Rich visual elements (emojis, formatting)
- Fallback template if gemini-cli unavailable
- Weekly summary generation

### 4. Data Manager (`modules/data_manager.py`)
- JSON-based persistence for responses and points
- Features:
  - Save/load questionnaire responses
  - Track points history with detailed breakdowns
  - Generate points trend visualizations (matplotlib)
  - Export data in JSON/CSV formats
  - Calculate statistics (total days, average points, study time, etc.)
  - Points table generation for easy viewing

## Important Implementation Details

### Scoring Rules Implementation
The system faithfully implements the scoring criteria from `resources/red_black_list.jpg`:
- Progressive rewards for longer study sessions
- Bonuses for completing more practice problems
- Lifestyle factors (sleep, diet, breaks) affect scores
- Penalties discourage unhealthy habits
- Streak bonuses reward consistency

### Data Storage Structure
```
data/
├── responses.json    # All questionnaire responses
└── points.json      # Points history and totals
```

### Report Generation Flow
1. User fills questionnaire → responses saved
2. Scoring system calculates points based on responses + history
3. Report generator creates prompt for gemini-cli
4. gemini-cli generates personalized content
5. Report saved as markdown (optionally converted to PDF)

### User Interface
- Command-line interface with clear menus
- Emoji-rich output for visual appeal
- Progress bars for level advancement
- Table views for points history
- Chart generation for visual progress tracking

## External Tool Requirements

- **gemini-cli**: Required for AI-powered report generation
- **matplotlib**: For generating progress charts
- **pandas**: For data manipulation and table generation
- **pandoc** (optional): For markdown to PDF conversion

## Usage Workflow

1. **Daily Check-in**: Run `pixi run python main.py` and select "填写今日问卷"
2. **View Reports**: Check generated reports in `reports/` directory
3. **Track Progress**: Use menu options to view points, statistics, and charts
4. **Weekly Review**: Generate weekly summaries for broader perspective
5. **Data Export**: Export data for backup or external analysis

## File Structure (Implemented)

```
diary/
├── main.py                 # Entry point with CLI interface
├── modules/
│   ├── __init__.py        # Package marker
│   ├── questionnaire.py    # Daily questionnaire generation
│   ├── scoring.py          # Points calculation logic
│   ├── report_generator.py # Report creation with gemini-cli
│   └── data_manager.py     # Data persistence and visualization
├── data/                   # User responses and points (auto-created)
├── reports/                # Generated reports (auto-created)
├── resources/              
│   └── red_black_list.jpg  # Scoring rules reference
├── README.md               # Project overview
├── CLAUDE.md              # This file
└── USAGE.md               # User guide (to be created)
```