#!/bin/bash

# Setup script for User Preference Learning feature
# This script helps you set up and test the preference learning system

set -e  # Exit on error

echo "=========================================="
echo "User Preference Learning - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check if we're in the right directory
echo "Step 1: Checking directory..."
if [ ! -f "backend/app/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi
print_success "Directory check passed"
echo ""

# Step 2: Check Python environment
echo "Step 2: Checking Python environment..."
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi
print_success "Python found: $(python --version)"
echo ""

# Step 3: Run database migration
echo "Step 3: Running database migration..."
echo "This will create the user_interactions and user_preferences tables"
echo ""

python backend/migrations/add_user_preference_tables.py status

echo ""
read -p "Do you want to apply the migration? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    python backend/migrations/add_user_preference_tables.py up
    if [ $? -eq 0 ]; then
        print_success "Migration applied successfully"
    else
        print_error "Migration failed"
        exit 1
    fi
else
    print_warning "Migration skipped"
fi
echo ""

# Step 4: Verify database tables
echo "Step 4: Verifying database tables..."
python -m app.models.init_db verify
if [ $? -eq 0 ]; then
    print_success "Database verification passed"
else
    print_error "Database verification failed"
    exit 1
fi
echo ""

# Step 5: Test API endpoints
echo "Step 5: Testing API endpoints..."
echo "Starting the API server in the background..."

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    print_warning "Server is already running on port 8000"
    SERVER_RUNNING=true
else
    print_warning "Please start the server manually with: uvicorn app.main:app --reload"
    print_warning "Then run the test commands below"
    SERVER_RUNNING=false
fi
echo ""

# Step 6: Show test commands
echo "Step 6: Test Commands"
echo "===================="
echo ""
echo "Once your server is running, test these endpoints:"
echo ""
echo "1. Track a user interaction:"
echo "   curl -X POST 'http://localhost:8000/api/user-interactions/' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"user_id\": \"test_user\", \"product_id\": 1, \"interaction_type\": \"view\", \"duration_seconds\": 30}'"
echo ""
echo "2. Get user statistics:"
echo "   curl 'http://localhost:8000/api/user-interactions/stats/test_user'"
echo ""
echo "3. Get preference weights:"
echo "   curl 'http://localhost:8000/api/user-interactions/preferences/test_user/weights'"
echo ""
echo "4. List interactions:"
echo "   curl 'http://localhost:8000/api/user-interactions/?user_id=test_user'"
echo ""

# Step 7: Show integration guide
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_success "User Preference Learning is ready to use"
echo ""
echo "📚 Next Steps:"
echo "   1. Read the integration guide: docs/USER_PREFERENCE_INTEGRATION_GUIDE.md"
echo "   2. Update your frontend to track user interactions"
echo "   3. Integrate PersonalizedScoreCalculator in your orchestrator"
echo "   4. Test with real user data"
echo ""
echo "📖 Documentation:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Integration Guide: docs/USER_PREFERENCE_INTEGRATION_GUIDE.md"
echo "   - Migration Plan: docs/AGENTIC_UPGRADE_PLAN.md"
echo ""
print_success "Happy coding! 🚀"

# Made with Bob
