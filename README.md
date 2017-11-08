
## Evedom

This is a lightweight python package designed to ease a bit more the use of `eve`.

Actually helping structuring eve endpoint(s) into an auto built domain and with all in one place.

### Installation

```bash
pip install evedom
```

### Settings.py

```python
import os.path as path
from evedom import loader

# ...

DOMAIN = loader.domain(root=path.dirname(__file__), folder='endpoints')
```

### Endpoint

Based on above settings, Endpoint(s) shall be set into
`'root/endpoints'` where root = path.dirname(\__file__).

```
root/
  endpoints/
    my_endpoint.py
    sub_folder/
      my_nested_endpoint.py
```

See below example to create an endpoint,
More example can be found in the [evedom demo](https://github.com/nam4dev/evedom_demo) project.

```python
from evedom import Endpoint

class Members(Endpoint):

    name = 'members'
    spec = {
        # by default the standard item entry point is defined as
        # '/member/<ObjectId>/'. We leave it untouched, and we also enable an
        # additional read-only entry point. This way consumers can also perform GET
        # requests at '/member/<email>/'.
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'email'
        },
        'public_methods': [],
        'public_item_methods': [],
        'datasource': {'default_sort': [('email', 1)]},
        # Schema definition, based on Cerberus grammar. Check the Cerberus project
        # (https://github.com/nicolaiarocci/cerberus) for details.
        'schema': {
            'firstname': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 60,
                'required': False,
            },
            'lastname': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 60,
                'required': False,
            },
            'token': {
                'type': 'string',
                'required': False,
            },
            'email': {
                'type': 'string',
                'minlength': 6,  # <1.letter>@<1.letter>.<2.letters>
                'maxlength': 128,
                # 'email' is an API entry-point, so we need it to be unique.
                'unique': True,
                'required': True
            },
            'password': {
                'type': 'string',
                'required': True,
            },
        }
    }

    @classmethod
    def encrypt_password(cls, password):
        """
        Encrypt given password

        Args:
            password (str): The Member's password

        Returns:
             str: An Encrypted password
        """
        # Encrypt password here
        my_encrypted_password = password

        return my_encrypted_password

    def _on_methods(self):
        """
        Based on Eve's event hooks framework,
        a set of callback can be intelligently assigned to
        specific events

        Returns:
            list: A set of callbacks mapped to Eve event hooks framework.
        """
        return [
            ('on_insert_{}'.format(self.name), self._on_insert),
            ('on_update_{}'.format(self.name), self._on_update),
            ('on_replace_{}'.format(self.name), self._on_update),
        ]

    def _on(self, members):
        """
        Common processing to apply on all cases
        (insert, update, replace)

        Args:
            members: A Collection of Member(s)
        """
        if not isinstance(members, (tuple, list)):
            members = [members]

        for member in members:
            member['password'] = self.encrypt_password(member['password'])

    def _on_insert(self, members):
        """
        On INSERT event Member's hook

        Args:
            members: A Collection of Member(s) about to be inserted
        """
        self._on(members)

    def _on_update(self, members, *_):
        """
        On UPDATE event Member's hook

        Args:
            members: The Collection of Member(s) reflecting its UPDATE state
            original_members: The Collection of Member(s) reflecting its ORIGINAL state
        """
        self._on(members)

    def _on_replace(self, members):
        """
        On REPLACE event Member's hook

        Args:
            members: A Collection of Member(s) just inserted
        """
        self._on(members)

    def _renew_member_password(self):
        """
        Authentication Route

        Returns:
            Renewal Result (JSON)
        """
        payload = json.loads(request.data.decode('utf8'))

        members = self.resources_by_name('members')

        # Seek for Member match
        member = members.find_one(payload)
        if not member:
            abort(401, "Invalid Credentials provided")

        new_password = 'GeneratedPassword'
        # Generate a fresh authentication password
        member['password'] = self.encrypt_password(new_password)

        # Create the body of the message (a plain-text and an HTML version).
        # resp = _mail_new_password(member)

        return self.dumps({'renewed': True}, indent=4)

    def _authenticate_member(self):
        """
        Authentication Route

        Returns:
            The Authenticated Member (JSON)
        """
        credentials = json.loads(request.data.decode('utf8'))

        members = self.resources_by_name('members')

        # Encrypt given password to match against db Query
        credentials['password'] = self.encrypt_password(credentials['password'])
        # Seek for Member match
        member = members.find_one(credentials)

        if not member:
            abort(401, "Invalid Credentials provided")

        # Generate a fresh authentication token...

        return self.dumps(member, indent=4)

    def _register_member(self):
        """
        Registration Route

        Returns:
            The Authenticated just created Member (JSON)
        """
        member_data = json.loads(request.data.decode('utf8'))

        # Register the Member

        member_data['token'] = "0123456789"
        del member_data['password']

        return self.dumps(member_data, indent=4)

    def _register(self):
        """
        Allow to register any custom endpoint
        """
        self.app.route(
            '/register/', methods=['POST']
        )(self._register_member)

        self.app.route(
            '/authenticate/', methods=['POST']
        )(self._authenticate_member)

        self.app.route(
            '/renew/password/', methods=['POST']
        )(self._renew_member_password)
```

That's all folks!