# SOAP Budget Approval System Mock - File Index

Complete file reference and quick navigation guide.

## Directory Structure

```
/Users/chocho/projects/STAGEHAND/mocks/soap-budget/
├── approvals.xml              - XML fixture data (20 budget approval records)
├── soap_server.py             - Flask + Spyne SOAP service implementation
├── requirements.txt           - Python package dependencies
├── Dockerfile                 - Docker container definition
├── docker-compose.yml         - Docker Compose configuration
├── README.md                  - Main documentation (450+ lines)
├── IMPLEMENTATION_SUMMARY.md  - Implementation details and architecture
├── EXAMPLE_USAGE.md          - Complete usage examples and patterns
├── QUICK_START.sh            - Automated testing bash script
├── test_soap_service.py      - Python integration test suite
└── INDEX.md                  - This file
```

## File Reference Guide

### Data Files

#### approvals.xml (11 KB)
**Purpose:** XML fixture containing 20 budget approval records

**Contains:**
- 20 complete approval records (APR-001 to APR-020)
- Campaign IDs matching Nike marketing campaigns
- Approved amounts: $715K to $5M
- Approval dates: Aug 18 - Oct 25, 2025
- Cost centers: US-MARKETING-DIGITAL, GLOBAL-BRAND
- Approver names and email addresses
- Budget status and approval notes

**Use Cases:**
- Data source for SOAP service
- Reference for expected response format
- Test data for integration testing
- Examples of budget approval structure

**Format:** XML, valid and well-formed
**Size:** 11 KB, ~200 lines

---

### Service Implementation

#### soap_server.py (11 KB)
**Purpose:** Flask + Spyne SOAP web service implementation

**Key Components:**
- `BudgetApproval` class - Data model
- `BudgetApprovalService` class - SOAP service with 3 RPC methods
- `load_approvals()` - Loads XML fixture into memory cache
- `create_app()` - Flask application factory

**Methods:**
1. `GetCampaignApprovals(dateFrom, dateTo)` - Date range query
2. `GetApprovalByID(approvalID)` - Single record lookup
3. `GetApprovalsByCostCenter(costCenter)` - Cost center summary

**Features:**
- SOAP 1.1 protocol
- XML persistence
- In-memory caching
- Date filtering and validation
- Error handling with descriptive messages
- WSDL endpoint support
- Health check integration

**Run:**
```bash
python soap_server.py
# Starts on http://localhost:5000
```

**Technologies:** Flask 3.0.0, Spyne 2.14.20, lxml 4.9.4

---

### Configuration Files

#### requirements.txt (40 bytes)
**Purpose:** Python package dependencies

**Contents:**
```
Flask==3.0.0
spyne==2.14.20
lxml==4.9.4
```

**Install:**
```bash
pip install -r requirements.txt
```

---

#### Dockerfile (659 bytes)
**Purpose:** Docker container definition

**Features:**
- Python 3.11 slim base image
- System dependencies (libxml2, libxslt1-dev)
- Python dependencies installation
- Health check endpoint
- Port 5000 exposure

**Build:**
```bash
docker build -t soap-budget-service .
```

**Run:**
```bash
docker run -p 5000:5000 soap-budget-service
```

---

#### docker-compose.yml (652 bytes)
**Purpose:** Docker Compose service orchestration

**Services:**
- soap-budget-service (main service)
  - Port mapping: 5000:5000
  - Volume mounts for development
  - Health check configuration
  - Auto-restart policy

**Run:**
```bash
docker-compose up -d
```

**Stop:**
```bash
docker-compose down
```

---

### Documentation

#### README.md (12 KB, 450+ lines)
**Purpose:** Complete service documentation

**Sections:**
1. Overview and architecture
2. Data model documentation
3. Installation instructions
4. API endpoints reference
5. 3 detailed SOAP request examples
6. Testing guide (curl, Python, Postman)
7. WSDL reference
8. Cost centers and status values
9. Integration notes
10. Troubleshooting guide
11. Performance metrics

**Read:** Start here for comprehensive documentation
```bash
cat README.md
```

---

#### IMPLEMENTATION_SUMMARY.md (14 KB)
**Purpose:** Implementation details and architecture notes

**Sections:**
1. What was created (file structure)
2. Approval fixture data (statistics)
3. Service endpoints (3 SOAP methods)
4. Key features implemented
5. Docker support details
6. Testing infrastructure
7. Requirements met (all 5)
8. Example request/response
9. Architecture highlights
10. Design patterns
11. Performance characteristics
12. Use cases
13. File purposes reference
14. Next steps/enhancements

**Read:** For architectural details and design decisions
```bash
cat IMPLEMENTATION_SUMMARY.md
```

---

#### EXAMPLE_USAGE.md (17 KB)
**Purpose:** Complete working examples and integration patterns

**Sections:**
1. Setup instructions
2. Example 1: Get September Approvals (with curl)
3. Example 2: Get Single Approval
4. Example 3: Get Cost Center Summary
5. Example 4: Date Range Queries
6. Example 5: Error Handling
7. Using Different Tools (Python, Postman, SoapUI)
8. Integration Patterns:
   - Budget approval dashboard
   - Cost center budget report
   - Approval verification

**Read:** For step-by-step working examples
```bash
cat EXAMPLE_USAGE.md
```

---

### Testing Scripts

#### QUICK_START.sh (6.2 KB)
**Purpose:** Automated bash testing script with 5 test cases

**Test Cases:**
1. Health check validation
2. Get Campaign Approvals (date range)
3. Get Approval by ID
4. Get Approvals by Cost Center
5. Get Non-existent Approval (error handling)

**Features:**
- Color-coded output (green/red/yellow)
- Service availability check
- XML response parsing
- Metadata extraction
- Summary report

**Run:**
```bash
bash QUICK_START.sh
```

**Requirements:** Service must be running

---

#### test_soap_service.py (6.6 KB)
**Purpose:** Python integration test suite

**Test Functions:**
1. `test_health_check()` - Health endpoint
2. `test_get_campaign_approvals()` - Date range query
3. `test_get_approval_by_id()` - Single record lookup
4. `test_get_approvals_by_cost_center()` - Cost center summary

**Features:**
- Pretty XML printing
- Response parsing
- Metadata extraction
- Error handling
- Connection validation
- Descriptive output

**Run:**
```bash
python test_soap_service.py
```

**Requirements:**
- Service running
- Python packages: requests, lxml

---

## Quick Start Guide

### 1. First Time Setup

```bash
# Navigate to directory
cd /Users/chocho/projects/STAGEHAND/mocks/soap-budget

# Install dependencies
pip install -r requirements.txt

# Start service
python soap_server.py

# In another terminal, verify it's running
curl http://localhost:5000/health
# Should return: {"status":"healthy"}
```

### 2. Quick Testing

```bash
# Option A: Run bash tests
bash QUICK_START.sh

# Option B: Run Python tests
python test_soap_service.py

# Option C: Manual curl test
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d @request.xml
```

### 3. View Documentation

```bash
# Main documentation
cat README.md

# Implementation details
cat IMPLEMENTATION_SUMMARY.md

# Working examples
cat EXAMPLE_USAGE.md

# This index
cat INDEX.md
```

### 4. Docker Deployment

```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose logs -f

# Stop
docker-compose down
```

## File Usage Matrix

| File | Purpose | When to Use | Run Command |
|------|---------|------------|-------------|
| approvals.xml | Data source | Reference fixture data | `cat approvals.xml` |
| soap_server.py | Service | Run server | `python soap_server.py` |
| requirements.txt | Dependencies | First time setup | `pip install -r requirements.txt` |
| Dockerfile | Containerization | Docker deployment | `docker build -t soap-budget-service .` |
| docker-compose.yml | Orchestration | Docker Compose deployment | `docker-compose up -d` |
| README.md | Documentation | Main reference | `cat README.md` |
| IMPLEMENTATION_SUMMARY.md | Architecture | Understand design | `cat IMPLEMENTATION_SUMMARY.md` |
| EXAMPLE_USAGE.md | Examples | Learn by example | `cat EXAMPLE_USAGE.md` |
| QUICK_START.sh | Testing | Quick validation | `bash QUICK_START.sh` |
| test_soap_service.py | Testing | Automated tests | `python test_soap_service.py` |
| INDEX.md | Navigation | Find what you need | `cat INDEX.md` |

## Common Tasks

### Start the Service
```bash
cd /Users/chocho/projects/STAGEHAND/mocks/soap-budget
python soap_server.py
```

### Get September 2025 Approvals
```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d @request.xml
```
(See EXAMPLE_USAGE.md for request.xml)

### Run All Tests
```bash
bash QUICK_START.sh
```

### View Fixture Data
```bash
cat approvals.xml | grep -A 5 "<Approval>"
```

### Check Service Status
```bash
curl http://localhost:5000/health
```

### View WSDL
```bash
curl http://localhost:5000/soap/BudgetService?wsdl
```

### Deploy with Docker
```bash
docker-compose up -d
```

## File Statistics

| Metric | Value |
|--------|-------|
| Total Files | 11 |
| Total Size | 112 KB |
| Largest File | README.md (12 KB) |
| Smallest File | requirements.txt (40 B) |
| Code Files | 2 (Python) |
| Data Files | 1 (XML) |
| Config Files | 3 |
| Docs Files | 4 |
| Test Files | 2 |

## Technology Stack

**Language:** Python 3.11

**Web Framework:** Flask 3.0.0

**SOAP Framework:** Spyne 2.14.20

**XML Processing:** lxml 4.9.4

**Container:** Docker

**Orchestration:** Docker Compose

**Testing:** bash, Python (requests library)

## Support and Troubleshooting

### Service Won't Start
1. Check Python installation: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Check port 5000: `netstat -an | grep 5000`
4. Use different port if needed (edit soap_server.py)

### Tests Fail
1. Verify service is running: `curl http://localhost:5000/health`
2. Check Python packages: `pip list | grep -E "Flask|spyne|lxml"`
3. Run with verbose output: `python test_soap_service.py`

### Docker Issues
1. Build image: `docker build -t soap-budget-service .`
2. Run with logs: `docker run -it -p 5000:5000 soap-budget-service`
3. Use compose: `docker-compose up` (no -d flag for debugging)

## Next Steps

1. Start the service (see "Common Tasks" above)
2. Read README.md for comprehensive documentation
3. Check EXAMPLE_USAGE.md for working examples
4. Run QUICK_START.sh for automated testing
5. Explore the SOAP methods with curl or Postman
6. Deploy with Docker when ready for production

## File Locations

All files are located at:
```
/Users/chocho/projects/STAGEHAND/mocks/soap-budget/
```

Individual files:
- Fixtures: `/Users/chocho/projects/STAGEHAND/mocks/soap-budget/approvals.xml`
- Service: `/Users/chocho/projects/STAGEHAND/mocks/soap-budget/soap_server.py`
- Config: `/Users/chocho/projects/STAGEHAND/mocks/soap-budget/requirements.txt`
- Docs: `/Users/chocho/projects/STAGEHAND/mocks/soap-budget/README.md`
- Tests: `/Users/chocho/projects/STAGEHAND/mocks/soap-budget/test_soap_service.py`

## License

This mock service is provided as part of the STAGEHAND project.

---

Last Updated: November 11, 2025
Version: 1.0
Status: Production Ready
