from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Creates a super admin user and organization'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--email', type=str, default='admin@connectflow.com', help='Admin email')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password')
        parser.add_argument('--org-name', type=str, default='ConnectFlow HQ', help='Organization name')
        parser.add_argument('--org-code', type=str, default='CFHQ', help='Organization code')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        org_name = options['org_name']
        org_code = options['org_code']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists!'))
            user = User.objects.get(username=username)
        else:
            # Create or get organization
            organization, created = Organization.objects.get_or_create(
                code=org_code,
                defaults={
                    'name': org_name,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created organization: {org_name} (Code: {org_code})'))
            else:
                self.stdout.write(self.style.WARNING(f'Organization "{org_name}" already exists'))

            # Create super admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User',
                role=User.Role.SUPER_ADMIN,
                organization=organization,
                is_staff=True,
                is_superuser=True,
                status=User.Status.ONLINE
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created super admin user: {username}'))

        # Display credentials
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('ADMIN ACCOUNT DETAILS'))
        self.stdout.write('='*60)
        self.stdout.write(f'Username:     {username}')
        self.stdout.write(f'Email:        {email}')
        self.stdout.write(f'Password:     {password}')
        self.stdout.write(f'Role:         {user.get_role_display()}')
        self.stdout.write(f'Organization: {user.organization.name if user.organization else "None"}')
        self.stdout.write(f'Org Code:     {user.organization.code if user.organization else "None"}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\n✓ Admin account is ready to use!'))
