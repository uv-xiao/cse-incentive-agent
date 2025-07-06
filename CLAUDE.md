# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Main Entry Point**: `main.py`  
**User Data Location**: `data/` directory  
**Reports Location**: `reports/` directory  
**Key Modules**:
- `modules/questionnaire.py` - Daily questions
- `modules/scoring.py` - Points calculation
- `modules/report_generator.py` - AI reports
- `modules/data_manager.py` - Data persistence
- `modules/redemption_system.py` - Rewards system

## Project Overview

This is a Civil Service Exam Study Agent (考公Agent) designed to support ZZW in their civil service exam preparation journey. The system provides daily questionnaires, generates encouraging summary reports, and maintains a points-based reward/punishment system to gamify the study process.

### Key Features
- 📋 Daily questionnaire system with comprehensive tracking
- 🎯 Points-based gamification with rewards and penalties
- 📊 AI-powered report generation using gemini-cli
- 📈 Progress visualization and statistics
- 🎁 Reward redemption system
- 📤 Excel export/import for non-technical users

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

## Incremental Updates

- Tell Claude to make changes about scoring rule and any other things, the Claude Code should synchronize the code changes and the USAGE.md should be updated.
- Always test changes before confirming completion
- Document all changes in both CLAUDE.md and USAGE.md
- Preserve user data when updating system rules

## Recent Updates (2025-01-06)

### Intelligent Answer Processing
- Added natural language answer support using gemini-cli
- System can now understand answers like "0 (don't deduct points!)" or "studied for 2 hours"
- Automatic semantic matching for better user experience
- Fallback mechanism ensures all answers are processed
- Real-time feedback on answer interpretation

### Practice Accuracy Tracking
- Added accuracy rate text input question (0-100)
- Scoring based on accuracy ranges:
  - 95%+: +8 points (excellent)
  - 90-94%: +6 points (very good)
  - 85-89%: +5 points (good)
  - 80-84%: +4 points (decent)
  - 75-79%: +3 points (passing)
  - 70-74%: +2 points (needs work)
  - 60-69%: +1 point (warning)
  - 50-59%: 0 points (poor)
  - 40-49%: -2 points (very poor)
  - 30-39%: -3 points (failing)
  - <30%: -5 points (critical)
- Only calculates accuracy points when problems were actually completed
- Supports various input formats: 85, 85%, 85.5

## Previous Updates (2025-07-06)

### Expanded Questionnaire Options
- Study time options now extend up to 480+ minutes (8+ hours)
- Practice problem options now extend up to 180+ problems
- Added thesis writing tracking (0-5000+ words daily)
- Added memorization time tracking (0-120+ minutes)
- Added online course viewing time tracking (0-180+ minutes)

### Enhanced Scoring System
- Extended study duration scoring: up to 15 points for 480+ minutes
- Extended practice problem scoring: up to 12 points for 180+ problems
- Added thesis writing scoring: 2-10 points based on word count
- Added memorization scoring: 1-6 points based on time spent
- Added online course scoring: 2-6 points based on viewing time

### Strengthened Penalty System (2025-07-06)
- Increased all penalties by 2-3x for stronger deterrent effect
- Added new penalties for not doing thesis/memorization/online courses
- Maximum daily penalty can now reach -30 points to encourage balanced study

These updates reflect ZZW's actual study patterns and provide better tracking for comprehensive exam preparation activities.

## Common User Requests and How to Handle Them

### 1. Adjusting Scoring Rules
```
User: "I want to increase points for studying 300 minutes"
Action: Edit modules/scoring.py, update the study_duration rules, then update USAGE.md
```

### 2. Adding New Questions
```
User: "Add a question about exercise time"
Action: Edit modules/questionnaire.py to add the question, then update scoring.py if needed
```

### 3. Modifying Rewards
```
User: "Add a new reward: bubble tea for 50 points"
Action: Edit modules/redemption_system.py, add to the rewards list
```

### 4. Fixing Data Issues
```
User: "My points seem wrong today"
Action: Check data/points.json and data/responses.json, recalculate if needed
```

### 5. Generating Special Reports
```
User: "Generate a monthly summary report"
Action: Use data_manager to gather data, then generate report with gemini-cli
```

## Code Style Guidelines

1. **Language**: All code comments and user-facing text should be in Chinese
2. **Emojis**: Use emojis liberally in user interfaces for visual appeal
3. **Error Handling**: Always provide friendly Chinese error messages
4. **Data Validation**: Validate all user inputs before processing
5. **File Organization**: Keep related functions in their respective modules

## Testing Approach

When making changes:
1. Test with edge cases (0 study time, maximum values)
2. Verify point calculations are correct
3. Check that reports generate properly
4. Ensure Excel import/export works correctly
5. Test that historical data is preserved

## Important Notes for Future Development

### User Context
- ZZW is preparing for civil service exams (考公)
- Also working on thesis writing simultaneously
- Studies for extended periods (often 6-8+ hours daily)
- Completes large numbers of practice problems (100+ daily)
- Values detailed tracking and encouragement

### System Design Principles
1. **Positive Reinforcement**: Focus on encouragement over criticism
2. **Flexibility**: Support various study patterns and schedules
3. **Data Integrity**: Never lose user data, always backup before modifications
4. **User-Friendly**: Design for non-technical users (Excel support)
5. **Comprehensive Tracking**: Track all aspects of exam preparation

### Common Pitfalls to Avoid
1. Don't hardcode date formats - use datetime properly
2. Don't assume gemini-cli is always available - have fallbacks
3. Don't overwrite historical data when updating rules
4. Don't forget to update USAGE.md when changing features
5. Don't remove features without user confirmation

## Debugging Tips

1. **Points calculation issues**: Check calculate_points() in scoring.py
2. **Excel import failures**: Verify column names match expected format
3. **Report generation errors**: Check if gemini-cli is installed and accessible
4. **Missing data**: Look in data/ directory for JSON files
5. **UI issues**: Check main.py menu logic

## Future Enhancement Ideas

1. **Mobile App Integration**: API for mobile questionnaire submission
2. **Study Group Features**: Compare progress with study partners
3. **Smart Reminders**: AI-powered study time suggestions
4. **Exam Countdown**: Special features as exam date approaches
5. **Practice Test Integration**: Track mock exam scores
6. **Study Material Management**: Organize and track study resources
7. **Voice Input**: Support voice answers for questionnaires
8. **Weekly/Monthly Challenges**: Special goals for bonus points