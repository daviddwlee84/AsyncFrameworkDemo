-- Create tasks table to store async tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    payload JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retries INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create notification function for new tasks
CREATE OR REPLACE FUNCTION notify_new_task()
RETURNS TRIGGER AS $$
BEGIN
    -- Send notification with task details
    PERFORM pg_notify(
        'new_task',
        json_build_object(
            'id', NEW.id,
            'type', NEW.type,
            'payload', NEW.payload,
            'created_at', NEW.created_at
        )::text
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for new task notifications
CREATE TRIGGER notify_new_task_trigger
    AFTER INSERT ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_task();

-- Create notification function for task status updates
CREATE OR REPLACE FUNCTION notify_task_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Only notify if status changed
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        PERFORM pg_notify(
            'task_update',
            json_build_object(
                'id', NEW.id,
                'old_status', OLD.status,
                'new_status', NEW.status,
                'result', NEW.result,
                'error_message', NEW.error_message,
                'updated_at', NEW.updated_at
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for task status update notifications
CREATE TRIGGER notify_task_update_trigger
    AFTER UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION notify_task_update();