#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input

# 배포 전 DB 백업
if python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; then
    python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json
    echo "DB 백업 완료: backup.json"
fi

python manage.py migrate

python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print('관리자 계정 생성 완료')
else:
    print('관리자 계정 이미 존재')
EOF
