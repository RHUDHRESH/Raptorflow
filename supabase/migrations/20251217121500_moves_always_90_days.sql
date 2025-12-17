DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_proc
    WHERE proname = 'enforce_moves_90_days'
  ) THEN
    CREATE FUNCTION public.enforce_moves_90_days()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF NEW.planned_start IS NOT NULL THEN
        NEW.planned_end := (NEW.planned_start + INTERVAL '90 days')::date;
      ELSIF NEW.planned_end IS NOT NULL THEN
        NEW.planned_start := (NEW.planned_end - INTERVAL '90 days')::date;
      END IF;

      RETURN NEW;
    END;
    $$;
  END IF;
END
$$;

DROP TRIGGER IF EXISTS trg_enforce_moves_90_days ON public.moves;

CREATE TRIGGER trg_enforce_moves_90_days
BEFORE INSERT OR UPDATE OF planned_start, planned_end
ON public.moves
FOR EACH ROW
EXECUTE FUNCTION public.enforce_moves_90_days();
