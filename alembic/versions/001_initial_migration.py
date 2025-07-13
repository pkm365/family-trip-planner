"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-12-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create trips table
    op.create_table('trips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('accommodation_address', sa.Text(), nullable=False),
        sa.Column('accommodation_lat', sa.Float(), nullable=True),
        sa.Column('accommodation_lon', sa.Float(), nullable=True),
        sa.Column('total_budget', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trips_id'), 'trips', ['id'], unique=False)
    op.create_index(op.f('ix_trips_name'), 'trips', ['name'], unique=False)
    op.create_index(op.f('ix_trips_start_date'), 'trips', ['start_date'], unique=False)
    op.create_index(op.f('ix_trips_end_date'), 'trips', ['end_date'], unique=False)

    # Create activities table
    op.create_table('activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trip_id', sa.Integer(), nullable=False),
        sa.Column('activity_date', sa.Date(), nullable=False),
        sa.Column('time_slot', sa.Enum('MORNING', 'AFTERNOON', 'EVENING', name='timeslot'), nullable=False),
        sa.Column('category', sa.Enum('SIGHTSEEING', 'FOOD', 'SHOPPING', 'REST', 'TRANSPORTATION', name='activitycategory'), nullable=False),
        sa.Column('priority', sa.Enum('MUST_DO', 'WOULD_LIKE', 'OPTIONAL', name='priority'), nullable=False),
        sa.Column('location_name', sa.String(length=200), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=False),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    op.create_index(op.f('ix_activities_trip_id'), 'activities', ['trip_id'], unique=False)
    op.create_index(op.f('ix_activities_activity_date'), 'activities', ['activity_date'], unique=False)

    # Create family_members table
    op.create_table('family_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('PARENT', 'CHILD', 'ADULT', name='memberrole'), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('trip_id', sa.Integer(), nullable=False),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('mobility_needs', sa.Text(), nullable=True),
        sa.Column('interests', sa.Text(), nullable=True),
        sa.Column('wishlist_items', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_family_members_id'), 'family_members', ['id'], unique=False)
    op.create_index(op.f('ix_family_members_trip_id'), 'family_members', ['trip_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_family_members_trip_id'), table_name='family_members')
    op.drop_index(op.f('ix_family_members_id'), table_name='family_members')
    op.drop_table('family_members')
    
    op.drop_index(op.f('ix_activities_activity_date'), table_name='activities')
    op.drop_index(op.f('ix_activities_trip_id'), table_name='activities')
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    
    op.drop_index(op.f('ix_trips_end_date'), table_name='trips')
    op.drop_index(op.f('ix_trips_start_date'), table_name='trips')
    op.drop_index(op.f('ix_trips_name'), table_name='trips')
    op.drop_index(op.f('ix_trips_id'), table_name='trips')
    op.drop_table('trips')