# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Analyzer is a multi-broker portfolio analysis application that integrates with Korean investment broker APIs (한국투자증권/KIS, 키움증권/Kiwoom) to automatically collect and analyze account data. The application features both a console interface and a Streamlit-based GUI for data visualization and analysis.

## Architecture

### Core Components

- **Broker System**: Abstract broker interface (`app/brokers/base_broker.py`) with concrete implementations (KIS broker, Kiwoom broker)
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

# Test Kiwoom API integration (Windows only)
python test_kiwoom_broker.py

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

# Kiwoom Securities API (Windows only)
KIWOOM_ACCOUNT_NUMBER=your_10_digit_account_number
KIWOOM_ACCOUNT_PASSWORD=your_account_password
KIWOOM_CERT_PASSWORD=your_certificate_password
KIWOOM_DELISTED_FILTER=0
KIWOOM_PASSWORD_MEDIA=00
KIWOOM_EXCHANGE_CODE=KRX

# Kiwoom TR Codes
KIWOOM_TR_BALANCE=opw00018
KIWOOM_TR_HOLDINGS=OPW00004
KIWOOM_TR_ACCOUNT_EVAL=opw00001

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
- **KIS (한국투자증권)**: REST API, token-based authentication
- **Kiwoom (키움증권)**: COM/ActiveX API (Windows only), session-based authentication
- Token files stored in `token/{broker_name}/tokens.json` (KIS only)
- Automatic token refresh when within 5 minutes of expiry (KIS only)

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

## Recent Updates

### 2025-10-01: Kiwoom Securities Integration (32-bit Subprocess Architecture)

#### Multi-Broker Architecture Implementation
- **New Broker**: Kiwoom Securities (키움증권) support added
- **Architecture**: 32-bit subprocess method (64-bit main + 32-bit worker)
- **Platform**: Windows only (requires Kiwoom OpenAPI+ module)

#### Key Features
1. **32-bit Subprocess Architecture**
   - Main program runs in 64-bit Python environment
   - Kiwoom API runs in separate 32-bit Python subprocess
   - Automatic subprocess execution on API calls
   - JSON-based IPC communication

2. **KiwoomBroker Class** (`app/brokers/kiwoom_broker.py`)
   - Implements `BaseBroker` interface
   - Subprocess management with timeout handling
   - Unified interface same as KIS broker
   - Account caching for performance

3. **Worker Script** (`kiwoom_worker_32.py`)
   - Standalone 32-bit Python script
   - QAxWidget-based COM object handling
   - Commands: get_accounts, get_balance, get_holdings
   - JSON output for easy parsing

4. **Environment Variable Management**
   - All Kiwoom settings in `env` file
   - `PYTHON32_PATH`: Path to 32-bit Python executable
   - TR codes configurable (OPW00004, opw00018, etc.)
   - Account credentials securely stored
   - No hardcoded values in source code

5. **TR Implementation**
   - **OPW00004**: Account evaluation status (계좌평가현황)
   - **opw00018**: Deposit details (예수금상세현황)
   - Profit rate calculation with 4-digit decimal handling

6. **BrokerService Integration**
   - Automatic broker type detection
   - Unified interface for KIS and Kiwoom
   - Same `get_balance()`, `get_holdings()` methods
   - Transparent subprocess execution

#### Technical Details
- **Main Program**: 64-bit Python (any version)
- **Worker Process**: 32-bit Python 3.9+ with pywin32==306, PyQt5==5.15.10
- **Communication**: subprocess.run() with JSON serialization
- **OCX Registration**: 32-bit regsvr32 in SysWOW64
- **Data Parsing**: Custom parsers for each TR response
- **Error Handling**: Comprehensive subprocess and COM error catching

#### Setup Guide
- Detailed setup instructions: `docs/KIWOOM_SETUP.md`
- 32-bit Python installation guide
- OCX registration procedure
- Environment variable configuration
- Troubleshooting tips

#### Requirements
1. Windows OS (64-bit)
2. 32-bit Python 3.9+ (separate installation)
3. Kiwoom OpenAPI+ module installed and registered
4. Valid Kiwoom account
5. HTS installation NOT required (OpenAPI+ module only)

#### Configuration Example
```json
{
  "name": "키움증권",
  "api_type": "kiwoom",
  "enabled": true,
  "platform": "windows"
}
```

```bash
# env file
PYTHON32_PATH=C:\Python39-32\python.exe
KIWOOM_ACCOUNT_NUMBER=1234567890
KIWOOM_ACCOUNT_PASSWORD=****
```

### 2025-09-30: Dashboard and Database Tools

### Database Commands Implementation
- **New Feature**: Comprehensive database viewing and analysis tools
- **Files Added**:
  - `view_database.py` - Main table viewer with filtering options
  - `db_commands.py` - Quick query commands
  - `db_analysis.py` - Advanced analysis tools
  - `db.bat` - Windows batch shortcuts
  - `show_table_columns.py` - Schema inspection tool
  - `DATABASE_COMMANDS.md` - Complete usage documentation
- **Capabilities**: View all 10 database tables with 149 total columns, perform portfolio analysis

### Data Collection Enhancement
- **Auto Collection**: Automatic account data retrieval when today's data is missing
- **Manual Collection**: Sidebar button for on-demand data collection from all active accounts
- **Location**: `gui/main.py` sidebar, `gui/pages_backup/dashboard.py`
- **Session Management**: Prevents duplicate data collection runs

### GUI Architecture Improvements
- **Transaction Features Disabled**: Removed transaction-related UI elements (API not implemented)
  - Removed "Transactions" menu from main navigation
  - Disabled transaction display in Dashboard
  - Removed "거래 패턴 분석" from Analysis charts
- **Dashboard Simplification**:
  - Removed chart functionality (moved to Analysis page)
  - Focus on key metrics display only
  - Added Analysis page navigation guidance
- **Chart Enhancements**:
  - Fixed date formatting (removed time information)
  - Improved chart margins and visibility
  - Updated "일일 수익률" → "일자별 수익률" for clarity
  - Enhanced color schemes for better data visualization

### Database Schema Verification
- **Normalization Check**: Confirmed proper database design with separated broker/account tables
- **Data Display**: Fixed UI to show broker and account information separately (not concatenated)
- **Schema Documentation**: Complete column listing for all 10 tables

### Key Metrics Improvements
- **Dashboard Metrics**: Clarified percentage displays
  - Total balance: Shows actual profit/loss rate
  - Cash balance: Shows portfolio weight percentage
  - Stock balance: Shows investment return rate
  - Holdings: Shows profitable holdings count

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