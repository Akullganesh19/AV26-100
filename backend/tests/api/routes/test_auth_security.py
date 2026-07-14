import pytest
from app.api.routes.auth import register
from app.schemas.user import UserCreate
from app.models.user import UserRole
from fastapi import Request
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_register_mass_assignment_mitigation():
    # Only verify the static signature and behavior without hitting the DB
    import ast
    with open('app/api/routes/auth.py', 'r') as f:
        tree = ast.parse(f.read())

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.role_hardcoded = False
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'User':
                for kw in node.keywords:
                    if kw.arg == 'role':
                        if isinstance(kw.value, ast.Attribute) and kw.value.attr == 'OFFICER':
                            self.role_hardcoded = True
            self.generic_visit(node)

    v = Visitor()
    v.visit(tree)
    assert v.role_hardcoded, "Role is not hardcoded to OFFICER in User creation"
