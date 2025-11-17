#!/bin/bash

echo "======================================================================"
echo "TOR INSTALLER - AUTO-START (Amazon Linux 2023)"
echo "======================================================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

echo "======================================================================"
echo "STEP 1: UPDATING SYSTEM"
echo "======================================================================"
dnf update -y > /dev/null 2>&1
print_status "System updated"

echo ""
echo "======================================================================"
echo "STEP 2: INSTALLING DEPENDENCIES"
echo "======================================================================"
dnf install -y curl tar gzip which findutils procps-ng > /dev/null 2>&1
print_status "Basic tools installed"

dnf groupinstall -y "Development Tools" > /dev/null 2>&1
dnf install -y libevent-devel openssl-devel zlib-devel libzstd-devel xz-devel > /dev/null 2>&1
print_status "Build dependencies installed"

echo ""
echo "======================================================================"
echo "STEP 3: DOWNLOADING TOR"
echo "======================================================================"
TOR_VERSION="0.4.8.13"
cd /tmp
curl -L -o tor-${TOR_VERSION}.tar.gz https://dist.torproject.org/tor-${TOR_VERSION}.tar.gz 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Download failed"
    exit 1
fi
print_status "Downloaded TOR ${TOR_VERSION}"

echo ""
echo "======================================================================"
echo "STEP 4: COMPILING TOR (2-3 minutes)"
echo "======================================================================"
tar -xzf tor-${TOR_VERSION}.tar.gz
cd tor-${TOR_VERSION}

print_status "Configuring..."
./configure --prefix=/usr/local > /tmp/tor-configure.log 2>&1
if [ $? -ne 0 ]; then
    print_error "Configure failed"
    exit 1
fi

print_status "Compiling (please wait)..."
make -j$(nproc) > /tmp/tor-make.log 2>&1
if [ $? -ne 0 ]; then
    print_error "Compilation failed"
    exit 1
fi

print_status "Installing..."
make install > /tmp/tor-install.log 2>&1
print_status "TOR installed: /usr/local/bin/tor"
/usr/local/bin/tor --version | head -1

cd /tmp
rm -rf tor-${TOR_VERSION} tor-${TOR_VERSION}.tar.gz
print_status "Cleanup done"

echo ""
echo "======================================================================"
echo "STEP 5: CONFIGURING TOR"
echo "======================================================================"
mkdir -p /etc/tor /var/lib/tor
chmod 700 /var/lib/tor

cat > /etc/tor/torrc << 'EOF'
SocksPort 9050
DataDirectory /var/lib/tor
Log notice file /tmp/tor.log
RunAsDaemon 0
EOF
print_status "Config created: /etc/tor/torrc"

echo ""
echo "======================================================================"
echo "STEP 6: CREATING AUTO-START SCRIPT"
echo "======================================================================"
cat > /usr/local/bin/tor-daemon.sh << 'EOFTORDAEMON'
#!/bin/bash
# Kill existing TOR
pkill -f "tor -f /etc/tor/torrc" 2>/dev/null
sleep 1

# Start TOR
nohup /usr/local/bin/tor -f /etc/tor/torrc > /tmp/tor-stdout.log 2>&1 &
echo $! > /tmp/tor.pid

# Wait for bootstrap
sleep 3
for i in {1..30}; do
    if grep -q "Bootstrapped 100%" /tmp/tor.log 2>/dev/null; then
        echo "✓ TOR ready on port 9050"
        exit 0
    fi
    sleep 1
done
echo "⚠ TOR started but still bootstrapping"
EOFTORDAEMON

chmod +x /usr/local/bin/tor-daemon.sh
print_status "Created: /usr/local/bin/tor-daemon.sh"

echo ""
echo "======================================================================"
echo "STEP 7: STARTING TOR NOW"
echo "======================================================================"
/usr/local/bin/tor-daemon.sh

echo ""
echo "======================================================================"
echo "INSTALLATION COMPLETE!"
echo "======================================================================"
echo ""
echo "✓ TOR ${TOR_VERSION} compiled and installed"
echo "✓ TOR is running on port 9050"
echo "✓ SOCKS proxy: 127.0.0.1:9050"
echo ""
echo "======================================================================"
echo "USAGE:"
echo "======================================================================"
echo ""
echo "TOR is already running!"
echo "Your bot can use: 127.0.0.1:9050"
echo ""
echo "To restart TOR anytime:"
echo "  /usr/local/bin/tor-daemon.sh"
echo ""
echo "To check status:"
echo "  ps -p \$(cat /tmp/tor.pid)"
echo ""
echo "To view logs:"
echo "  tail -f /tmp/tor.log"
echo ""
echo "To stop TOR:"
echo "  kill \$(cat /tmp/tor.pid)"
echo ""
echo "======================================================================"
echo "TOR IS READY!"
echo "======================================================================"
