"""Added Sample Tables.

Revision ID: a9e9660843ab
Revises:
Create Date: 2022-07-05 23:18:36.888864

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a9e9660843ab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=256), nullable=False, comment='author name'),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_authors')),
                    sa.UniqueConstraint('name', name=op.f('uq_authors_name'))
                    )
    op.create_table('books',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('title', sa.String(length=256), nullable=False, comment='book title'),
                    sa.Column('author_id', sa.Integer(), nullable=False),
                    sa.Column('isbn', sa.String(length=13), nullable=False, comment='book isbn'),
                    sa.Column('cover_path', sa.String(length=256), server_default='none',
                              nullable=False, comment='book cover path'),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], name=op.f('fk_books_author_id_authors')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_books')),
                    sa.UniqueConstraint('cover_path', name=op.f('uq_books_cover_path')),
                    sa.UniqueConstraint('isbn', name=op.f('uq_books_isbn'))
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('books')
    op.drop_table('authors')
    # ### end Alembic commands ###
