"""adicao da view historico

Revision ID: cd1662cb70e6
Revises: a5e81fe533eb
Create Date: 2026-02-01 14:57:37.616360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd1662cb70e6'
down_revision = 'a5e81fe533eb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE VIEW vw_historico_retiradas AS
        SELECT
            r.retirada_id,
            r.data_retirada,
            r.hora_retirada,
            r.hora_prevista_devolucao,
            r.hora_devolucao,
            r.status,

            s.sala_id,
            s.sala_nome,

            c.chave_id,
            c.chave_nome,

            resp.responsavel_id,
            resp.responsavel_nome
        FROM tb_retirada r
        JOIN tb_chave c ON c.chave_id = r.chave_id
        JOIN tb_sala s ON s.sala_id = c.sala_id
        JOIN tb_responsavel resp ON resp.responsavel_id = r.responsavel_id
        WHERE r.status = 'finalizada';
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS vw_historico_retiradas")