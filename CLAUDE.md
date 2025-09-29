# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Analyzer is a multi-broker portfolio analysis application that integrates with Korean investment broker APIs (primarily 한국투자증권/KIS) to automatically collect and analyze account data. The application features both a console interface and a Streamlit-based GUI for data visualization and analysis.

## Architecture

### Core Components

- **Broker System**: Abstract broker interface (`app/brokers/base_broker.py`) with concrete implementations (KIS broker)
- **Database Layer**: SQLAlchemy ORM models for accounts, balances, holdings, transactions, and aggregation data
- **Service Layer**: Business logic in `app/services/` (BrokerService, DataCollector, AnalysisService)
- **Token Management**: Secure, broker-specific token handling with automatic refresh (`app/utils/token_manager.py`)
- **Configuration**: Environment-based config with JSON settings and .env file support
- **GUI Interface**: Streamlit-based web interface with interactive charts and data tables

### Key Design Patterns

- **Multi-Broker Architecture**: Extensible broker system supporting multiple investment platforms
- **Token Security**: Broker-specific token storage in `token/{broker}/tokens.json` with automatic expiry management
- **Environment Configuration**: Sensitive credentials via environment variables, general settings via JSON
- **Error Handling**: Custom exceptions with comprehensive logging and sensitive data masking
- **Data Aggregation**: Separate models for monthly summaries, performance analysis, and risk metrics

## Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy env.example to env and configure)
# Required: KIS_APP_KEY, KIS_APP_SECRET
# Optional: EMAIL_USERNAME, EMAIL_PASSWORD for notifications
```

### Running the Application
```bash
# Main console application
python main.py

# Streamlit GUI (runs on http://localhost:8501)
python run_gui.py

# Alternative GUI launch
streamlit run gui/main.py --server.port 8501
```

### Token Management
```bash
# Check token status for all brokers
python manage_tokens.py status

# Clear all tokens
python manage_tokens.py clear

# Delete specific broker tokens
python manage_tokens.py delete "kis"
python manage_tokens.py delete "kiwoom"
```

### Testing and Validation
```bash
# Test token management system
python test_token_manager.py

# Test KIS API integration
python test_kis_api.py

# Test with real data (requires valid credentials)
python test_with_real_data.py

# Test GUI data services
python test_gui_data.py

# Check database structure and connections
python check_database.py
```

## Configuration

### Environment Variables (env file)
```bash
# Korean Investment Securities API
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret

# Optional: Email notifications
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### Database Configuration
- Default: SQLite database at `./data/stock_analyzer.db`
- Models: Account, DailyBalance, Holding, Transaction, plus aggregation tables
- Automatic schema creation on first run

### Broker Configuration
- Settings in `config/config.json` under `brokers` array
- Token files stored in `token/{broker_name}/tokens.json`
- Automatic token refresh when within 5 minutes of expiry

## Code Structure Patterns

### Adding New Brokers
1. Implement `BaseBroker` interface in `app/brokers/`
2. Add broker configuration to `config/config.json`
3. Update `BrokerService` to recognize new broker type
4. Create corresponding token directory structure

### Database Models
- All models inherit from `app.utils.database.Base`
- Use relationships for data integrity
- Include `created_at`/`updated_at` timestamps
- Follow naming convention: `tablename` as plural snake_case

### Service Layer
- Services handle business logic and database operations
- Use dependency injection for broker instances
- Include comprehensive error handling and logging
- Return structured data dictionaries for API consistency

### Token Management
- Broker-specific TokenManager instances
- Automatic expiry checking with configurable threshold
- JSON storage with ISO datetime formats
- Thread-safe token refresh operations

## GUI Development

### Streamlit Application Structure
- Main app: `gui/main.py`
- Page modules: `gui/pages_backup/` (dashboard, accounts, holdings, transactions, analysis)
- Data services: `gui/utils/data_service.py`
- Chart services: `gui/utils/chart_service.py`

### Data Visualization
- Plotly integration for interactive charts
- Chart generation: `app/utils/chart_generator.py`
- Export formats: HTML, PNG, PDF support
- Responsive design with container width adaptation

## Testing Approach

### Test Files
- `test_token_manager.py`: Token management validation
- `test_kis_api.py`: API connection and data retrieval testing
- `test_with_real_data.py`: End-to-end testing with real broker data
- `test_gui_data.py`: GUI data service validation

### Testing Patterns
- Integration tests for broker connections
- Mock data for UI component testing
- Real API testing with valid credentials
- Database schema validation

## Security Considerations

### Sensitive Data Handling
- API keys and secrets in environment variables only
- Token files excluded from version control
- Automatic sensitive data masking in logs
- Secure token storage with expiry management

### Git Exclusions
- `env` file (contains API keys)
- `token/` directory (contains access tokens)
- `data/` directory (contains database files)
- `logs/` directory (contains application logs)

## Common Development Tasks

### Adding New Analysis Features
1. Create new model in `app/models/aggregation.py` if needed
2. Implement analysis logic in `app/services/analysis_service.py`
3. Add GUI components in appropriate page module
4. Update chart generator for new visualizations

### Debugging Broker Issues
1. Check token status: `python manage_tokens.py status`
2. Verify environment variables in `env` file
3. Review logs in `logs/stock_analyzer.log`
4. Test API connection: `python test_kis_api.py`

### Database Modifications
1. Update model definitions in `app/models/`
2. Ensure proper relationships and constraints
3. Test with `python check_database.py`
4. Consider data migration for existing installations

## Recent Updates (2024-09-30)

### Welcome Dashboard Implementation
- **New Feature**: Implemented welcome dashboard for initial user experience
- **Location**: `gui/pages_backup/dashboard.py:show_welcome_dashboard()`
- **Purpose**: Provides comprehensive onboarding experience when no account is selected
- **Components**:
  - Welcome message and application introduction
  - Feature overview (3-column layout)
  - Step-by-step usage guide
  - Account registration status display
  - FAQ and technical stack information
  - Footer with version info

### Documentation Structure
- **Added**: Comprehensive documentation system in `docs/` directory
- **Structure**:
  ```
  docs/
  ├── README.md              # Documentation overview
  ├── gui/
  │   └── dashboard.md       # Detailed dashboard documentation
  ├── architecture.md        # System architecture (planned)
  ├── development.md         # Development guidelines (planned)
  └── user-guide.md         # User manual (planned)
  ```

### GUI Enhancements
- **Initial Screen**: Enhanced user experience for first-time users
- **Account Detection**: Automatic detection of registered accounts
- **Guidance System**: Clear instructions for getting started
- **Visual Improvements**: Better layout and styling for welcome screen