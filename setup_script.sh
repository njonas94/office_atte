#!/bin/bash

# Employee Attendance Dashboard Setup Script
echo "🚀 Setting up Employee Attendance Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Create directory structure
setup_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p backend/reports
    mkdir -p frontend/src/components
    mkdir -p frontend/public
    
    print_status "Directory structure created ✓"
}

# Create environment file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp .env.example .env
        print_warning "Please edit .env file with your Oracle database credentials"
        print_warning "Configuration needed: ORACLE_HOST, ORACLE_USER, ORACLE_PASSWORD, etc."
    else
        print_status "Environment file exists ✓"
    fi
}

# Check TNS configuration
check_tns() {
    if [ ! -f tnsnames.ora ]; then
        print_warning "tnsnames.ora not found. If using TNS, please place your tnsnames.ora file in the project root."
        
        # Create a sample tnsnames.ora
        cat > tnsnames.ora << 'EOF'
# Sample TNS Configuration
# Replace with your actual TNS configuration
YOUR_TNS_ALIAS =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = your_host)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = your_service_name)
    )
  )
EOF
        print_status "Sample tnsnames.ora created. Please update with your configuration."
    else
        print_status "TNS configuration file found ✓"
    fi
}

# Build and start services
build_and_start() {
    print_status "Building Docker images..."
    docker-compose build
    
    if [ $? -eq 0 ]; then
        print_status "Images built successfully ✓"
    else
        print_error "Failed to build images"
        exit 1
    fi
    
    print_status "Starting services..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status "Services started successfully ✓"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    echo -n "Waiting for backend API"
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/dashboard-stats > /dev/null 2>&1; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for frontend
    echo -n "Waiting for frontend"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 2
    done
}

# Display final information
show_info() {
    echo
    print_status "🎉 Setup completed successfully!"
    echo
    echo "Access your application:"
    echo "  📊 Dashboard: http://localhost:3000"
    echo "  🔧 API Docs:  http://localhost:8000/docs"
    echo "  📈 API Base:  http://localhost:8000/api"
    echo
    echo "Useful commands:"
    echo "  📋 View logs:           docker-compose logs -f"
    echo "  🔄 Restart services:   docker-compose restart"
    echo "  🛑 Stop services:      docker-compose down"
    echo "  🔍 Check status:       docker-compose ps"
    echo
    print_warning "Remember to configure your Oracle database credentials in .env file"
    echo
}

# Health check function
health_check() {
    print_status "Running health check..."
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Containers are running ✓"
    else
        print_error "Some containers are not running properly"
        docker-compose ps
    fi
    
    # Check API endpoint
    if curl -s http://localhost:8000/api/dashboard-stats > /dev/null; then
        print_status "Backend API is responding ✓"
    else
        print_warning "Backend API is not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend is responding ✓"
    else
        print_warning "Frontend is not responding"
    fi
}

# Main setup process
main() {
    echo "Employee Attendance Dashboard Setup"
    echo "===================================="
    echo
    
    check_docker
    setup_directories
    setup_env
    check_tns
    
    # Ask user if they want to proceed
    echo
    read -p "Ready to build and start services? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_and_start
        wait_for_services
        health_check
        show_info
    else
        print_status "Setup prepared. Run 'docker-compose up -d' when ready."
    fi
}

# Handle command line arguments
case "${1:-}" in
    "health")
        health_check
        ;;
    "start")
        docker-compose up -d
        wait_for_services
        show_info
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "rebuild")
        print_status "Rebuilding services..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        main
        ;;
esac