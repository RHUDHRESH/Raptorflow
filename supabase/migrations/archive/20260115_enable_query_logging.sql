-- Enable Query Logging for Performance Analysis
-- Migration: 20260115_enable_query_logging.sql
-- No-cost solution for database performance monitoring

-- Enable pg_stat_statements extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Configure query logging for performance analysis
-- Track slow queries (> 1 second) and high-frequency queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
ALTER SYSTEM SET log_statement = 'all';  -- Log all statements for analysis
ALTER SYSTEM SET log_duration = on;  -- Log query duration
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- Configure pg_stat_statements for query analysis
ALTER SYSTEM SET pg_stat_statements.max = 10000;  -- Track 10,000 unique queries
ALTER SYSTEM SET pg_stat_statements.track = 'all';  -- Track all queries
ALTER SYSTEM SET pg_stat_statements.track_utility = on;  -- Track utility commands
ALTER SYSTEM SET pg_stat_statements.save = on;  -- Save stats across restarts

-- Reload configuration
SELECT pg_reload_conf();

-- Create view for slow query analysis
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
WHERE mean_exec_time > 1.0  -- Queries slower than 1 second
ORDER BY mean_exec_time DESC;

-- Create view for high-frequency queries
CREATE OR REPLACE VIEW frequent_queries AS
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements 
WHERE calls > 100  -- Queries called more than 100 times
ORDER BY calls DESC;

-- Create view for missing indexes analysis
CREATE OR REPLACE VIEW missing_indexes AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
  AND n_distinct > 10  -- Columns with many distinct values
  AND correlation < 0.9  -- Poor correlation indicates need for index
ORDER BY n_distinct DESC;

-- Grant access to monitoring views
GRANT SELECT ON slow_queries TO authenticated;
GRANT SELECT ON frequent_queries TO authenticated;
GRANT SELECT ON missing_indexes TO authenticated;

-- Create function to get query performance summary
CREATE OR REPLACE FUNCTION get_query_performance_summary()
RETURNS TABLE(
    total_queries BIGINT,
    slow_queries BIGINT,
    avg_query_time FLOAT,
    total_exec_time FLOAT,
    top_slow_query TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_queries,
        COUNT(*) FILTER (WHERE mean_exec_time > 1.0) as slow_queries,
        AVG(mean_exec_time) as avg_query_time,
        SUM(total_exec_time) as total_exec_time,
        (SELECT query FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 1) as top_slow_query
    FROM pg_stat_statements;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to analyze query patterns
CREATE OR REPLACE FUNCTION analyze_query_patterns()
RETURNS TABLE(
    pattern_type TEXT,
    recommendation TEXT,
    priority TEXT
) AS $$
BEGIN
    RETURN QUERY
    -- Check for missing indexes
    SELECT 
        'MISSING_INDEX' as pattern_type,
        'Consider adding index on ' || schemaname || '.' || tablename || '(' || attname || ')' as recommendation,
        CASE 
            WHEN n_distinct > 1000 THEN 'HIGH'
            WHEN n_distinct > 100 THEN 'MEDIUM'
            ELSE 'LOW'
        END as priority
    FROM missing_indexes
    LIMIT 5
    
    UNION ALL
    
    -- Check for slow queries
    SELECT 
        'SLOW_QUERY' as pattern_type,
        'Optimize query: ' || LEFT(query, 100) || '...' as recommendation,
        CASE 
            WHEN mean_exec_time > 5.0 THEN 'HIGH'
            WHEN mean_exec_time > 2.0 THEN 'MEDIUM'
            ELSE 'LOW'
        END as priority
    FROM slow_queries
    LIMIT 5
    
    UNION ALL
    
    -- Check for high-frequency queries
    SELECT 
        'HIGH_FREQUENCY' as pattern_type,
        'Consider caching: ' || LEFT(query, 100) || '...' as recommendation,
        CASE 
            WHEN calls > 1000 THEN 'HIGH'
            WHEN calls > 500 THEN 'MEDIUM'
            ELSE 'LOW'
        END as priority
    FROM frequent_queries
    LIMIT 5;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create automated cleanup function for old query stats
CREATE OR REPLACE FUNCTION cleanup_old_query_stats()
RETURNS void AS $$
BEGIN
    -- Reset pg_stat_statements if it gets too large
    SELECT pg_stat_statements_reset();
    
    -- Log the cleanup
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        created_at
    ) VALUES (
        NULL,
        'cleanup_query_stats',
        'maintenance',
        'Cleaned up old query statistics',
        NOW()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-query-stats', '0 2 * * *', 'SELECT cleanup_old_query_stats();');

COMMENT ON VIEW slow_queries IS 'Queries with average execution time > 1 second';
COMMENT ON VIEW frequent_queries IS 'Queries executed more than 100 times';
COMMENT ON VIEW missing_indexes IS 'Columns that may benefit from additional indexes';
COMMENT ON FUNCTION get_query_performance_summary() IS 'Returns overall query performance metrics';
COMMENT ON FUNCTION analyze_query_patterns() IS 'Analyzes query patterns and provides optimization recommendations';
COMMENT ON FUNCTION cleanup_old_query_stats() IS 'Cleans up old query statistics to prevent bloat';
