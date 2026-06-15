--
-- PostgreSQL database dump
--

\restrict 1pv5ovVsCkVCyOoPFDT3xJXPWvxl30GkHofYkSg6C9KwvFNxV3tyOneeWDEUqTS

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.activity_logs OWNER TO postgres;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_logs_id_seq OWNER TO postgres;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: announcements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcements (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    image character varying(255),
    link character varying(255),
    priority character varying(50),
    status character varying(50),
    start_date date,
    end_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.announcements OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.announcements_id_seq OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    admin_id integer,
    action character varying(255) NOT NULL,
    details text,
    ip_address character varying(45),
    module character varying(100),
    before_value text,
    after_value text,
    created_at timestamp without time zone
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: authors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.authors (
    id integer NOT NULL,
    fullname character varying(120) NOT NULL
);


ALTER TABLE public.authors OWNER TO postgres;

--
-- Name: authors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.authors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.authors_id_seq OWNER TO postgres;

--
-- Name: authors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.authors_id_seq OWNED BY public.authors.id;


--
-- Name: book_copies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book_copies (
    id integer NOT NULL,
    book_id integer NOT NULL,
    nn_number character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.book_copies OWNER TO postgres;

--
-- Name: book_copies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.book_copies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.book_copies_id_seq OWNER TO postgres;

--
-- Name: book_copies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.book_copies_id_seq OWNED BY public.book_copies.id;


--
-- Name: book_reads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book_reads (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    first_read_at timestamp without time zone NOT NULL
);


ALTER TABLE public.book_reads OWNER TO postgres;

--
-- Name: book_reads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.book_reads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.book_reads_id_seq OWNER TO postgres;

--
-- Name: book_reads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.book_reads_id_seq OWNED BY public.book_reads.id;


--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    id integer NOT NULL,
    book_type character varying(20) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    isbn character varying(30),
    language character varying(50),
    published_year integer,
    cover_image character varying(255),
    rating double precision,
    category_id integer,
    author_id integer,
    created_at timestamp without time zone
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: books_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.books_id_seq OWNER TO postgres;

--
-- Name: books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.books_id_seq OWNED BY public.books.id;


--
-- Name: borrow_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.borrow_history (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    copy_id integer,
    borrowed_at timestamp without time zone NOT NULL,
    return_date timestamp without time zone NOT NULL,
    returned_at timestamp without time zone,
    final_fine_amount integer NOT NULL,
    fine_status character varying(20) NOT NULL,
    return_condition character varying(20) NOT NULL,
    condition_notes text,
    status character varying(20) NOT NULL
);


ALTER TABLE public.borrow_history OWNER TO postgres;

--
-- Name: borrow_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.borrow_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.borrow_history_id_seq OWNER TO postgres;

--
-- Name: borrow_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.borrow_history_id_seq OWNED BY public.borrow_history.id;


--
-- Name: borrow_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.borrow_requests (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    request_date timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL
);


ALTER TABLE public.borrow_requests OWNER TO postgres;

--
-- Name: borrow_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.borrow_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.borrow_requests_id_seq OWNER TO postgres;

--
-- Name: borrow_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.borrow_requests_id_seq OWNED BY public.borrow_requests.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: competition_books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competition_books (
    id integer NOT NULL,
    competition_id integer NOT NULL,
    book_id integer NOT NULL
);


ALTER TABLE public.competition_books OWNER TO postgres;

--
-- Name: competition_books_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competition_books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competition_books_id_seq OWNER TO postgres;

--
-- Name: competition_books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competition_books_id_seq OWNED BY public.competition_books.id;


--
-- Name: competition_certificates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competition_certificates (
    id integer NOT NULL,
    attempt_id integer NOT NULL,
    user_id integer NOT NULL,
    competition_id integer NOT NULL,
    "position" integer NOT NULL,
    score integer NOT NULL,
    percentage double precision NOT NULL,
    pdf_path character varying(255),
    verification_code character varying(32) NOT NULL,
    issued_at timestamp without time zone NOT NULL
);


ALTER TABLE public.competition_certificates OWNER TO postgres;

--
-- Name: competition_certificates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competition_certificates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competition_certificates_id_seq OWNER TO postgres;

--
-- Name: competition_certificates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competition_certificates_id_seq OWNED BY public.competition_certificates.id;


--
-- Name: competition_faculties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competition_faculties (
    id integer NOT NULL,
    competition_id integer NOT NULL,
    faculty_id integer NOT NULL
);


ALTER TABLE public.competition_faculties OWNER TO postgres;

--
-- Name: competition_faculties_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competition_faculties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competition_faculties_id_seq OWNER TO postgres;

--
-- Name: competition_faculties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competition_faculties_id_seq OWNED BY public.competition_faculties.id;


--
-- Name: competition_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competition_groups (
    id integer NOT NULL,
    competition_id integer NOT NULL,
    group_name character varying(100) NOT NULL
);


ALTER TABLE public.competition_groups OWNER TO postgres;

--
-- Name: competition_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competition_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competition_groups_id_seq OWNER TO postgres;

--
-- Name: competition_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competition_groups_id_seq OWNED BY public.competition_groups.id;


--
-- Name: competition_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competition_questions (
    id integer NOT NULL,
    competition_id integer NOT NULL,
    question_id integer NOT NULL,
    points_override integer,
    sort_order integer NOT NULL
);


ALTER TABLE public.competition_questions OWNER TO postgres;

--
-- Name: competition_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competition_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competition_questions_id_seq OWNER TO postgres;

--
-- Name: competition_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competition_questions_id_seq OWNED BY public.competition_questions.id;


--
-- Name: digital_books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.digital_books (
    id integer NOT NULL,
    pdf_file character varying(255) NOT NULL,
    pages integer,
    file_size integer,
    view_count integer,
    reading_count integer,
    allow_download boolean,
    online_read_only boolean
);


ALTER TABLE public.digital_books OWNER TO postgres;

--
-- Name: faculties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faculties (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.faculties OWNER TO postgres;

--
-- Name: faculties_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.faculties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.faculties_id_seq OWNER TO postgres;

--
-- Name: faculties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.faculties_id_seq OWNED BY public.faculties.id;


--
-- Name: favorite_books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorite_books (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.favorite_books OWNER TO postgres;

--
-- Name: favorite_books_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.favorite_books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.favorite_books_id_seq OWNER TO postgres;

--
-- Name: favorite_books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.favorite_books_id_seq OWNED BY public.favorite_books.id;


--
-- Name: impersonation_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.impersonation_logs (
    id integer NOT NULL,
    superadmin_id integer NOT NULL,
    target_user_id integer NOT NULL,
    ip_address character varying(45),
    started_at timestamp without time zone,
    ended_at timestamp without time zone
);


ALTER TABLE public.impersonation_logs OWNER TO postgres;

--
-- Name: impersonation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.impersonation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.impersonation_logs_id_seq OWNER TO postgres;

--
-- Name: impersonation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.impersonation_logs_id_seq OWNED BY public.impersonation_logs.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL,
    type character varying(50),
    is_read boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: pdf_bookmarks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pdf_bookmarks (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    page_number integer NOT NULL,
    note text,
    created_at timestamp without time zone
);


ALTER TABLE public.pdf_bookmarks OWNER TO postgres;

--
-- Name: pdf_bookmarks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pdf_bookmarks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pdf_bookmarks_id_seq OWNER TO postgres;

--
-- Name: pdf_bookmarks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pdf_bookmarks_id_seq OWNED BY public.pdf_bookmarks.id;


--
-- Name: physical_books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.physical_books (
    id integer NOT NULL,
    quantity integer,
    available_quantity integer,
    borrow_count integer,
    library_location character varying(120),
    shelf_code character varying(50)
);


ALTER TABLE public.physical_books OWNER TO postgres;

--
-- Name: question_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.question_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.question_categories OWNER TO postgres;

--
-- Name: question_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.question_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.question_categories_id_seq OWNER TO postgres;

--
-- Name: question_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.question_categories_id_seq OWNED BY public.question_categories.id;


--
-- Name: quiz_attempt_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_attempt_answers (
    id integer NOT NULL,
    attempt_id integer NOT NULL,
    question_id integer NOT NULL,
    selected_option_ids text,
    is_correct boolean NOT NULL,
    points_earned integer NOT NULL,
    options_order_json text
);


ALTER TABLE public.quiz_attempt_answers OWNER TO postgres;

--
-- Name: quiz_attempt_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_attempt_answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_attempt_answers_id_seq OWNER TO postgres;

--
-- Name: quiz_attempt_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_attempt_answers_id_seq OWNED BY public.quiz_attempt_answers.id;


--
-- Name: quiz_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_attempts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    competition_id integer NOT NULL,
    attempt_number integer NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    correct_count integer NOT NULL,
    wrong_count integer NOT NULL,
    score integer NOT NULL,
    max_score integer NOT NULL,
    percentage double precision NOT NULL,
    completion_seconds integer,
    ranking_score double precision NOT NULL,
    rank_position integer,
    medal character varying(20),
    focus_loss_count integer NOT NULL,
    fullscreen_exit_count integer NOT NULL,
    violation_count integer NOT NULL,
    question_order_json text
);


ALTER TABLE public.quiz_attempts OWNER TO postgres;

--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_attempts_id_seq OWNER TO postgres;

--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_attempts_id_seq OWNED BY public.quiz_attempts.id;


--
-- Name: quiz_question_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_question_options (
    id integer NOT NULL,
    question_id integer NOT NULL,
    option_text character varying(500) NOT NULL,
    is_correct boolean NOT NULL,
    sort_order integer NOT NULL
);


ALTER TABLE public.quiz_question_options OWNER TO postgres;

--
-- Name: quiz_question_options_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_question_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_question_options_id_seq OWNER TO postgres;

--
-- Name: quiz_question_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_question_options_id_seq OWNED BY public.quiz_question_options.id;


--
-- Name: quiz_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_questions (
    id integer NOT NULL,
    question_text text NOT NULL,
    question_type character varying(30) NOT NULL,
    category_id integer,
    image_path character varying(255),
    book_id integer,
    explanation text,
    points integer NOT NULL,
    difficulty character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    is_archived boolean NOT NULL,
    created_by_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.quiz_questions OWNER TO postgres;

--
-- Name: quiz_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_questions_id_seq OWNER TO postgres;

--
-- Name: quiz_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_questions_id_seq OWNED BY public.quiz_questions.id;


--
-- Name: quiz_violations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quiz_violations (
    id integer NOT NULL,
    attempt_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    details text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quiz_violations OWNER TO postgres;

--
-- Name: quiz_violations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quiz_violations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_violations_id_seq OWNER TO postgres;

--
-- Name: quiz_violations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quiz_violations_id_seq OWNED BY public.quiz_violations.id;


--
-- Name: reading_competitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reading_competitions (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    image_path character varying(255),
    competition_type character varying(30) NOT NULL,
    status character varying(20) NOT NULL,
    visibility character varying(20) NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    max_attempts integer NOT NULL,
    passing_score integer NOT NULL,
    time_limit_minutes integer,
    top_winners_count integer NOT NULL,
    randomize_questions boolean NOT NULL,
    randomize_answers boolean NOT NULL,
    prevent_reopen_completed boolean NOT NULL,
    secure_quiz_mode boolean NOT NULL,
    enable_watermark boolean NOT NULL,
    disable_copy boolean NOT NULL,
    disable_print boolean NOT NULL,
    require_fullscreen boolean NOT NULL,
    track_focus_loss boolean NOT NULL,
    track_devtools boolean NOT NULL,
    created_by_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.reading_competitions OWNER TO postgres;

--
-- Name: reading_competitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reading_competitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reading_competitions_id_seq OWNER TO postgres;

--
-- Name: reading_competitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reading_competitions_id_seq OWNED BY public.reading_competitions.id;


--
-- Name: reading_progress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reading_progress (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    current_page integer,
    updated_at timestamp without time zone
);


ALTER TABLE public.reading_progress OWNER TO postgres;

--
-- Name: reading_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reading_progress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reading_progress_id_seq OWNER TO postgres;

--
-- Name: reading_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reading_progress_id_seq OWNED BY public.reading_progress.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    user_id integer NOT NULL,
    book_id integer NOT NULL,
    rating integer NOT NULL,
    comment text,
    created_at timestamp without time zone
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_id_seq OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(255)
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value character varying(255) NOT NULL,
    description text
);


ALTER TABLE public.settings OWNER TO postgres;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settings_id_seq OWNER TO postgres;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: site_banners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.site_banners (
    id integer NOT NULL,
    enabled boolean,
    banner_text text NOT NULL,
    banner_type character varying(50),
    banner_icon character varying(50),
    scroll_speed character varying(50),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.site_banners OWNER TO postgres;

--
-- Name: site_banners_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.site_banners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.site_banners_id_seq OWNER TO postgres;

--
-- Name: site_banners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.site_banners_id_seq OWNED BY public.site_banners.id;


--
-- Name: user_badges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_badges (
    id integer NOT NULL,
    user_id integer NOT NULL,
    competition_id integer,
    badge_type character varying(30) NOT NULL,
    label character varying(120) NOT NULL,
    awarded_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_badges OWNER TO postgres;

--
-- Name: user_badges_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_badges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_badges_id_seq OWNER TO postgres;

--
-- Name: user_badges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_badges_id_seq OWNED BY public.user_badges.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    fullname character varying(120) NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    phone_number character varying(30),
    faculty character varying(120),
    faculty_id integer,
    group_name character varying(80),
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    role_id integer,
    avatar character varying(255),
    email_verified boolean NOT NULL,
    last_login_at timestamp without time zone,
    last_activity_at timestamp without time zone,
    is_blocked boolean NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: announcements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: authors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors ALTER COLUMN id SET DEFAULT nextval('public.authors_id_seq'::regclass);


--
-- Name: book_copies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_copies ALTER COLUMN id SET DEFAULT nextval('public.book_copies_id_seq'::regclass);


--
-- Name: book_reads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_reads ALTER COLUMN id SET DEFAULT nextval('public.book_reads_id_seq'::regclass);


--
-- Name: books id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books ALTER COLUMN id SET DEFAULT nextval('public.books_id_seq'::regclass);


--
-- Name: borrow_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_history ALTER COLUMN id SET DEFAULT nextval('public.borrow_history_id_seq'::regclass);


--
-- Name: borrow_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_requests ALTER COLUMN id SET DEFAULT nextval('public.borrow_requests_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: competition_books id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_books ALTER COLUMN id SET DEFAULT nextval('public.competition_books_id_seq'::regclass);


--
-- Name: competition_certificates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates ALTER COLUMN id SET DEFAULT nextval('public.competition_certificates_id_seq'::regclass);


--
-- Name: competition_faculties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_faculties ALTER COLUMN id SET DEFAULT nextval('public.competition_faculties_id_seq'::regclass);


--
-- Name: competition_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_groups ALTER COLUMN id SET DEFAULT nextval('public.competition_groups_id_seq'::regclass);


--
-- Name: competition_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_questions ALTER COLUMN id SET DEFAULT nextval('public.competition_questions_id_seq'::regclass);


--
-- Name: faculties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faculties ALTER COLUMN id SET DEFAULT nextval('public.faculties_id_seq'::regclass);


--
-- Name: favorite_books id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_books ALTER COLUMN id SET DEFAULT nextval('public.favorite_books_id_seq'::regclass);


--
-- Name: impersonation_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_logs ALTER COLUMN id SET DEFAULT nextval('public.impersonation_logs_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: pdf_bookmarks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_bookmarks ALTER COLUMN id SET DEFAULT nextval('public.pdf_bookmarks_id_seq'::regclass);


--
-- Name: question_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_categories ALTER COLUMN id SET DEFAULT nextval('public.question_categories_id_seq'::regclass);


--
-- Name: quiz_attempt_answers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempt_answers ALTER COLUMN id SET DEFAULT nextval('public.quiz_attempt_answers_id_seq'::regclass);


--
-- Name: quiz_attempts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts ALTER COLUMN id SET DEFAULT nextval('public.quiz_attempts_id_seq'::regclass);


--
-- Name: quiz_question_options id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_question_options ALTER COLUMN id SET DEFAULT nextval('public.quiz_question_options_id_seq'::regclass);


--
-- Name: quiz_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_questions ALTER COLUMN id SET DEFAULT nextval('public.quiz_questions_id_seq'::regclass);


--
-- Name: quiz_violations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_violations ALTER COLUMN id SET DEFAULT nextval('public.quiz_violations_id_seq'::regclass);


--
-- Name: reading_competitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_competitions ALTER COLUMN id SET DEFAULT nextval('public.reading_competitions_id_seq'::regclass);


--
-- Name: reading_progress id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_progress ALTER COLUMN id SET DEFAULT nextval('public.reading_progress_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: site_banners id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_banners ALTER COLUMN id SET DEFAULT nextval('public.site_banners_id_seq'::regclass);


--
-- Name: user_badges id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_badges ALTER COLUMN id SET DEFAULT nextval('public.user_badges_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity_logs (id, user_id, action, created_at) FROM stdin;
1	1	Logged in	2026-06-11 17:28:16.147931
2	1	Created admin account for admin	2026-06-11 17:29:16.410045
3	1	Created librarian account for librarian	2026-06-11 17:30:27.259462
4	1	Imported 20 users for faculty Artificial Intelligence (0 skipped of 20 rows)	2026-06-11 17:35:25.324944
5	1	Imported 19 users for faculty Data Science (1 skipped of 20 rows)	2026-06-11 17:41:59.130475
6	2	Logged out	2026-06-11 17:43:40.270283
7	32	Logged in	2026-06-11 17:43:54.393993
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
73eb893b0d5b
\.


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcements (id, title, description, image, link, priority, status, start_date, end_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, admin_id, action, details, ip_address, module, before_value, after_value, created_at) FROM stdin;
1	1	DATABASE_DELETE_BACKUP	Deleted backup: backup_20260611_160834.zip	127.0.0.1	database	\N	\N	2026-06-11 17:58:45.692621
2	1	FILE_DELETED	Deleted file: certificates/cert_FC096F3BFC2F5AA2.pdf	127.0.0.1	files	\N	\N	2026-06-12 10:01:06.559448
\.


--
-- Data for Name: authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.authors (id, fullname) FROM stdin;
1	Michael T. Goodrich
2	Michael T
8	Goodrich
9	Stuart Russell
\.


--
-- Data for Name: book_copies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.book_copies (id, book_id, nn_number, status, created_at) FROM stdin;
1	1	NN-2026-001	available	2026-06-12 08:52:45.90141
2	1	NN-2026-002	available	2026-06-12 08:52:45.90141
3	1	NN-2026-003	available	2026-06-12 08:52:45.90141
4	1	NN-2026-004	available	2026-06-12 08:52:45.90141
5	1	NN-2026-005	available	2026-06-12 08:52:45.90141
6	2	NN-2026-006	available	2026-06-12 08:55:11.074941
7	2	NN-2026-007	available	2026-06-12 08:55:11.074941
8	2	NN-2026-008	available	2026-06-12 08:55:11.074941
9	2	NN-2026-009	available	2026-06-12 08:55:11.074941
10	3	NN-202-0011	available	2026-06-12 08:59:57.791703
11	3	NN-202-0021	available	2026-06-12 08:59:57.791703
12	3	NN-202-0031	available	2026-06-12 08:59:57.791703
13	3	NN-202-0041	available	2026-06-12 08:59:57.791703
14	3	NN-202-0051	available	2026-06-12 08:59:57.791703
15	3	NN-202-00211	available	2026-06-12 08:59:57.791703
16	3	NN-202-00311	available	2026-06-12 08:59:57.791703
17	3	NN-202-00511	available	2026-06-12 08:59:57.791703
18	4	NN-2026-0012	available	2026-06-12 09:02:07.498219
19	4	NN-2026-0021	available	2026-06-12 09:02:07.498219
20	4	NN-2026-0033	available	2026-06-12 09:02:07.498219
21	4	NN-2026-0044	available	2026-06-12 09:02:07.498219
22	4	NN-2026-0055	available	2026-06-12 09:02:07.498219
23	4	NN-2026-0016	available	2026-06-12 09:02:07.498219
24	4	NN-2026-0027	available	2026-06-12 09:02:07.498219
25	4	NN-2026-0038	available	2026-06-12 09:02:07.498219
26	4	NN-2026-0049	available	2026-06-12 09:02:07.498219
27	4	NN-2026-0051	available	2026-06-12 09:02:07.498219
28	5	NN-2026-101	available	2026-06-12 09:04:55.763684
29	5	NN-2026-102	available	2026-06-12 09:04:55.763684
30	5	NN-2026-103	available	2026-06-12 09:04:55.763684
31	5	NN-2026-104	available	2026-06-12 09:04:55.763684
32	5	NN-2026-105	available	2026-06-12 09:04:55.763684
33	6	NN-2026-00121	available	2026-06-12 09:06:08.581316
34	6	NN-2026-00221	available	2026-06-12 09:06:08.581316
35	6	NN-2026-00321	available	2026-06-12 09:06:08.581316
36	6	NN-2026-00421	available	2026-06-12 09:06:08.581316
37	6	NN-2026-00521	available	2026-06-12 09:06:08.581316
38	7	NN-2026-1	available	2026-06-12 09:08:35.6272
39	7	NN-2026-2	available	2026-06-12 09:08:35.6272
40	7	NN-2026-3	available	2026-06-12 09:08:35.6272
41	7	NN-2026-4	available	2026-06-12 09:08:35.6272
42	7	NN-2026-5	available	2026-06-12 09:08:35.6272
43	7	NN-2026-6	available	2026-06-12 09:08:35.6272
44	8	NN-2026-0	available	2026-06-12 09:11:43.69891
45	8	NN-2026-01	available	2026-06-12 09:11:43.69891
46	8	NN-2026-02	available	2026-06-12 09:11:43.69891
47	9	NN-001	available	2026-06-12 09:13:50.483837
48	9	NN-002	available	2026-06-12 09:13:50.483837
50	9	NN-004	available	2026-06-12 09:13:50.483837
51	9	NN-005	available	2026-06-12 09:13:50.483837
52	10	N11	available	2026-06-12 09:15:38.25204
53	10	N12	available	2026-06-12 09:15:38.25204
54	10	N13	available	2026-06-12 09:15:38.25204
49	9	NN-003	borrowed	2026-06-12 09:13:50.483837
\.


--
-- Data for Name: book_reads; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.book_reads (id, user_id, book_id, first_read_at) FROM stdin;
1	32	18	2026-06-12 14:27:44.829435
\.


--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.books (id, book_type, title, description, isbn, language, published_year, cover_image, rating, category_id, author_id, created_at) FROM stdin;
1	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290279	English	2013	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612085245873409.jpg	0	16	1	2026-06-12 08:52:45.875408
2	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290270	uzbek	2012	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612085511067965.jpg	0	15	2	2026-06-12 08:55:11.068934
3	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290278	rus	2010	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612085957783667.jpg	0	5	8	2026-06-12 08:59:57.785669
4	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290277	rus	2010	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612090207495255.jpg	0	2	8	2026-06-12 09:02:07.496225
5	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290276	uzbek	2021	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612090455755657.jpg	0	15	1	2026-06-12 09:04:55.760679
6	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290275	uzbek	2020	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612090608578316.jpg	0	3	8	2026-06-12 09:06:08.579316
7	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	1315446468484846464	uzbek	2009	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612090835622345.jpg	0	2	1	2026-06-12 09:08:35.624345
8	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290271	uzbek	2012	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612091143695944.jpg	0	2	2	2026-06-12 09:11:43.696953
10	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290273	uzbek	2002	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612091538249046.jpg	0	1	8	2026-06-12 09:15:38.251041
11	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610993	English	2021	uploads/covers/Capture_20260612092328733099.PNG	0	16	9	2026-06-12 09:23:28.735084
12	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610992	English	2012	uploads/covers/Capture_20260612092505489461.PNG	0	16	9	2026-06-12 09:25:05.49046
13	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610991	uzbek	2014	uploads/covers/Capture_20260612092809750435.PNG	0	16	9	2026-06-12 09:28:09.75444
14	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610990	uzbek	2025	uploads/covers/Capture_20260612094111316012.PNG	0	16	9	2026-06-12 09:41:11.326047
15	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610994	uzbek	2003	uploads/covers/Capture_20260612094459281224.PNG	0	15	9	2026-06-12 09:44:59.287197
16	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610995	uzbek	2004	uploads/covers/Capture_20260612094552662227.PNG	0	15	9	2026-06-12 09:45:52.667279
17	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610993	uzbek	2000	uploads/covers/Capture_20260612094733995652.PNG	0	15	9	2026-06-12 09:47:34.000673
18	digital	Artificial Intelligence: A Modern Approach	Comprehensive introduction to artificial intelligence including search algorithms, machine learning, neural networks, knowledge representation, natural language processing, robotics, and modern AI applications. Suitable for undergraduate and graduate students.	9780134610996	English	2022	uploads/covers/Capture_20260612094848533832.PNG	0	15	9	2026-06-12 09:48:48.536832
9	physical	Data Structures and Algorithms in Python	Comprehensive guide to data structures, algorithms, complexity analysis, recursion, sorting, searching, trees, graphs, and practical Python implementations. Suitable for undergraduate students in computer science and software engineering.	9781118290272	uzbek	2002	uploads/covers/81g8vUXGSHL._UF10001000_QL80__20260612091350475836.jpg	5	16	1	2026-06-12 09:13:50.478868
\.


--
-- Data for Name: borrow_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.borrow_history (id, user_id, book_id, copy_id, borrowed_at, return_date, returned_at, final_fine_amount, fine_status, return_condition, condition_notes, status) FROM stdin;
1	32	9	49	2026-06-12 13:11:09.89964	2026-06-14 13:11:09.89964	\N	0	none	good	\N	Borrowed
\.


--
-- Data for Name: borrow_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.borrow_requests (id, user_id, book_id, request_date, status) FROM stdin;
1	32	9	2026-06-12 10:37:02.857696	Approved
2	32	10	2026-06-12 14:51:04.448949	Pending
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name) FROM stdin;
1	Data Science
2	Programming
3	Computer Networks
4	Cyber Security
5	Artificial Intelligence
6	Mathematics
7	Physics
8	Business & Management
9	English Language
10	Literature
11	Database Systems
12	Deep Learning
13	Machine Learning
14	Mobile Development
15	test Category
16	Computer Science
\.


--
-- Data for Name: competition_books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competition_books (id, competition_id, book_id) FROM stdin;
\.


--
-- Data for Name: competition_certificates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competition_certificates (id, attempt_id, user_id, competition_id, "position", score, percentage, pdf_path, verification_code, issued_at) FROM stdin;
1	1	32	1	1	6	66.7	uploads\\certificates/cert_6D8A8BF000B32AA1.pdf	6D8A8BF000B32AA1	2026-06-12 15:03:54.80348
\.


--
-- Data for Name: competition_faculties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competition_faculties (id, competition_id, faculty_id) FROM stdin;
\.


--
-- Data for Name: competition_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competition_groups (id, competition_id, group_name) FROM stdin;
\.


--
-- Data for Name: competition_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competition_questions (id, competition_id, question_id, points_override, sort_order) FROM stdin;
1	1	1	\N	1
2	1	2	\N	2
3	1	3	\N	3
\.


--
-- Data for Name: digital_books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.digital_books (id, pdf_file, pages, file_size, view_count, reading_count, allow_download, online_read_only) FROM stdin;
11	uploads/pdfs/AI_20260612092328682076.pdf	\N	\N	0	0	f	t
12	uploads/pdfs/AI_20260612092505449514.pdf	\N	\N	0	0	f	t
13	uploads/pdfs/AI_20260612092809700435.pdf	\N	\N	0	0	t	f
14	uploads/pdfs/AI_20260612094111262979.pdf	\N	\N	0	0	f	t
15	uploads/pdfs/AI_20260612094459228199.pdf	\N	\N	0	0	f	t
16	uploads/pdfs/AI_20260612094552611227.pdf	\N	\N	0	0	t	f
17	uploads/pdfs/AI_20260612094733946079.pdf	\N	\N	0	0	f	t
18	uploads/pdfs/AI_20260612094848476825.pdf	\N	\N	1	0	t	f
\.


--
-- Data for Name: faculties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.faculties (id, name, created_at) FROM stdin;
1	Computer Engineering	2026-06-11 17:31:06.813431
2	Data Science	2026-06-11 17:31:20.751499
3	Artificial Intelligence	2026-06-11 17:31:48.63765
\.


--
-- Data for Name: favorite_books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.favorite_books (id, user_id, book_id, created_at) FROM stdin;
\.


--
-- Data for Name: impersonation_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.impersonation_logs (id, superadmin_id, target_user_id, ip_address, started_at, ended_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, message, type, is_read, created_at) FROM stdin;
2	2	New borrow request for 'Data Structures and Algorithms in Python' from Shohjahon Sobirov.	info	f	2026-06-12 10:37:02.873697
1	32	Borrow request for 'Data Structures and Algorithms in Python' sent successfully.	info	t	2026-06-12 10:37:02.864674
3	3	New borrow request for 'Data Structures and Algorithms in Python' from Shohjahon Sobirov.	info	t	2026-06-12 10:37:02.873697
4	32	Your borrow request for 'Data Structures and Algorithms in Python' has been approved. Return deadline: 14 Jun 2026.	success	t	2026-06-12 13:11:09.924687
6	2	New borrow request for 'Data Structures and Algorithms in Python' from Shohjahon Sobirov.	info	f	2026-06-12 14:51:04.460439
7	3	New borrow request for 'Data Structures and Algorithms in Python' from Shohjahon Sobirov.	info	t	2026-06-12 14:51:04.460439
5	32	Borrow request for 'Data Structures and Algorithms in Python' sent successfully.	info	t	2026-06-12 14:51:04.45744
\.


--
-- Data for Name: pdf_bookmarks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pdf_bookmarks (id, user_id, book_id, page_number, note, created_at) FROM stdin;
\.


--
-- Data for Name: physical_books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.physical_books (id, quantity, available_quantity, borrow_count, library_location, shelf_code) FROM stdin;
1	5	5	0	Main Library Hall A	CS-A12-03
2	4	4	0	Main Library Hall A	CS-A12-03
3	8	8	0	Main Library Hall A	CS-A12-03
4	10	10	0	Main Library Hall A	CS-A12-03
5	5	5	0	Main Library Hall A	Shelf Code
6	5	5	0	main hall	m 12
7	6	6	0	Library Location	Shelf Code
8	3	3	0	Main Library Hall A	CS-A12-03
10	3	3	0	Main Library Hall A	CS-A12-03
9	5	4	1	Main Library Hall A	CS-A12-03
\.


--
-- Data for Name: question_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.question_categories (id, name, description, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: quiz_attempt_answers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_attempt_answers (id, attempt_id, question_id, selected_option_ids, is_correct, points_earned, options_order_json) FROM stdin;
2	1	1	[1]	f	0	\N
1	1	3	[9]	t	3	\N
3	1	2	[7, 5]	t	3	\N
\.


--
-- Data for Name: quiz_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_attempts (id, user_id, competition_id, attempt_number, status, started_at, completed_at, correct_count, wrong_count, score, max_score, percentage, completion_seconds, ranking_score, rank_position, medal, focus_loss_count, fullscreen_exit_count, violation_count, question_order_json) FROM stdin;
1	32	1	1	completed	2026-06-12 15:03:34.818578	2026-06-12 15:03:54.771905	2	1	6	9	66.7	19	66698.1	1	gold	0	0	0	[3, 1, 2]
\.


--
-- Data for Name: quiz_question_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_question_options (id, question_id, option_text, is_correct, sort_order) FROM stdin;
1	1	a javob	f	0
2	1	b javob	t	1
3	1	c javob	f	2
4	1	d javob	f	3
5	2	a	t	0
6	2	b	f	1
7	2	c	t	2
8	2	d	f	3
9	3	True	t	0
10	3	False	f	1
\.


--
-- Data for Name: quiz_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_questions (id, question_text, question_type, category_id, image_path, book_id, explanation, points, difficulty, is_active, is_archived, created_by_id, created_at, updated_at) FROM stdin;
1	test savol 1	single_choice	\N	\N	\N	\N	3	medium	t	f	3	2026-06-12 15:02:33.286789	2026-06-12 15:02:33.286789
2	test savol 2	multiple_choice	\N	\N	\N	\N	3	medium	t	f	3	2026-06-12 15:02:33.290793	2026-06-12 15:02:33.290793
3	true va false	true_false	\N	\N	\N	\N	3	medium	t	f	3	2026-06-12 15:02:33.298695	2026-06-12 15:02:33.298695
\.


--
-- Data for Name: quiz_violations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quiz_violations (id, attempt_id, event_type, details, created_at) FROM stdin;
\.


--
-- Data for Name: reading_competitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reading_competitions (id, title, description, image_path, competition_type, status, visibility, start_date, end_date, max_attempts, passing_score, time_limit_minutes, top_winners_count, randomize_questions, randomize_answers, prevent_reopen_completed, secure_quiz_mode, enable_watermark, disable_copy, disable_print, require_fullscreen, track_focus_loss, track_devtools, created_by_id, created_at, updated_at) FROM stdin;
1	Test quiz title	short description for competition	uploads/competitions/competition_2e1aae8d49334db2bb6e657dc217d6ce.png	university	published	public	2026-06-12 14:59:00	2026-06-13 15:00:00	1	60	10	3	t	t	f	f	f	f	f	f	f	f	3	2026-06-12 15:02:33.265091	2026-06-12 15:02:33.265091
\.


--
-- Data for Name: reading_progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reading_progress (id, user_id, book_id, current_page, updated_at) FROM stdin;
1	32	18	6	2026-06-12 14:28:13.306906
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (id, user_id, book_id, rating, comment, created_at) FROM stdin;
1	32	9	5	salommm	2026-06-12 14:30:01.154163
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.settings (id, key, value, description) FROM stdin;
\.


--
-- Data for Name: site_banners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.site_banners (id, enabled, banner_text, banner_type, banner_icon, scroll_speed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_badges; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_badges (id, user_id, competition_id, badge_type, label, awarded_at) FROM stdin;
1	32	1	gold	Gold - Test quiz title	2026-06-12 15:03:54.797498
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, fullname, username, email, phone_number, faculty, faculty_id, group_name, password_hash, role, role_id, avatar, email_verified, last_login_at, last_activity_at, is_blocked, created_at) FROM stdin;
1	Super Administrator	jaloliddin	jaloliddinomonboev@gmail.com	\N	\N	\N	\N	pbkdf2:sha256:600000$lObgOTpNGzyxTNnk$dedb17ce87fdff9dac19ac412bce0b50d1ea5273db4a31434bcc22fa2e1de4fc	superadmin	\N	\N	t	2026-06-11 17:28:16.142939	2026-06-11 17:28:16.142939	f	2026-06-11 17:23:59.286783
2	Admin	admin	admin@gmail.com	998883361308	\N	\N	\N	pbkdf2:sha256:600000$yJn1xZc8Hsstz0r6$dcb910bd9ef5d00005b7fb18a5432420a08576427f31c4720a8d1ead35ee659b	admin	\N	\N	f	\N	\N	f	2026-06-11 17:29:16.410045
3	Librarian	librarian	librarian@gmail.com	998883361307	\N	\N	\N	pbkdf2:sha256:600000$xRDHeB755LgBXA3a$e5a9dcbaf82b459a50115a9b02cac366632388299b95d0a2a99f2adb4466f8f8	librarian	\N	\N	f	\N	\N	f	2026-06-11 17:30:27.259462
4	Azizbek Karimov	azizbekkarimov33	azizbek.karimov@gmail.com	998901112233	Artificial Intelligence	3	CS-201	pbkdf2:sha256:600000$iuwUstN0MiIf9apo$075c87c0a0708a3c954d76413c8e01e5128d4ad3dcbf8acce7053b498f329725	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:16.704521
5	Dilshod Raximov	dilshodraximov34	dilshod.raximov@gmail.com	998901112234	Artificial Intelligence	3	CS-201	pbkdf2:sha256:600000$1E9QfECwOBYdtDN6$2502b6a1e00c90d30c86c8bfadcb068ce4612f2f0748323d07de7939aae0e299	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:17.160993
6	Shahzod Yusupov	shahzodyusupov35	shahzod.yusupov@gmail.com	998901112235	Artificial Intelligence	3	CS-202	pbkdf2:sha256:600000$RlwZsnt8HmUuq4Go$9be86caae860ee5a44ece47953b0e27c0331afa0f414aa3f6083dceba0eb66c6	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:17.59899
7	Bekzod Ismoilov	bekzodismoilov36	bekzod.ismoilov@gmail.com	998901112236	Artificial Intelligence	3	CS-202	pbkdf2:sha256:600000$B6X5YvDls0QS6q69$293784dd338c2a67b776540b58e93d6d403f2707c2b3934eb8bcd22fd94da2d8	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:18.065485
8	Jamshid Qodirov	jamshidqodirov37	jamshid.qodirov@gmail.com	998901112237	Artificial Intelligence	3	CS-203	pbkdf2:sha256:600000$qOfFzXgpRMipxpeJ$c06fda0607086f62328bb90ff7fd3e87972e4906afc4f87baea9d6477748ebbc	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:18.513905
9	Nodirbek Sobirov	nodirbeksobirov38	nodirbek.sobirov@gmail.com	998901112238	Artificial Intelligence	3	CS-203	pbkdf2:sha256:600000$Hy04VA4zDnbIUyNz$daf01ba18592c7812a3deee6876419c6346211d4e7ef8e92f090aa7879c80cce	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:18.974014
10	Muhammadali Tursunov	muhammadalitursunov39	muhammadali.tursunov@gmail.com	998901112239	Artificial Intelligence	3	CS-204	pbkdf2:sha256:600000$3LfmvJHLwQcmIFmC$6cf53078e368be9a7f99d6da59a1f61d3c0e2ce3f353bcf7e12f0f1242e5d45a	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:19.427561
11	Abdulaziz Ergashev	abdulazizergashev40	abdulaziz.ergashev@gmail.com	998901112240	Artificial Intelligence	3	CS-204	pbkdf2:sha256:600000$5BYEowILFacuErjG$281db42d5c56453f69555ffcbba7d81000db51148e91506c6f2f773c82e6ea44	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:19.864582
12	Doston Matkarimov	dostonmatkarimov41	doston.matkarimov@gmail.com	998901112241	Artificial Intelligence	3	CS-205	pbkdf2:sha256:600000$P8oG6syp9kD2soaz$c5953f337c2e299970d23ebbd91c2efe7941c0ae8dbc0c52479b32349dfb08eb	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:20.333679
13	Farrux Xudoyberdiyev	farruxxudoyberdiyev42	farrux.xudoyberdiyev@gmail.com	998901112242	Artificial Intelligence	3	CS-205	pbkdf2:sha256:600000$5mqmze0k9sy1cYOz$b601f90e45b1482772cbf8969f67d8239768265961679af74280a4aa0219aa76	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:20.779489
14	Maftuna Axmedova	maftunaaxmedova43	maftuna.axmedova@gmail.com	998901112243	Artificial Intelligence	3	CS-206	pbkdf2:sha256:600000$ZcgxQ7A0He8aqFa8$0dcfedf5a89a330244b1e49f9471e1b7c921a02dae629bf9aa66a90e8705c6ba	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:21.238626
15	Nilufar Jumaniyozova	nilufarjumaniyozova44	nilufar.jumaniyozova@gmail.com	998901112244	Artificial Intelligence	3	CS-206	pbkdf2:sha256:600000$tuTkLE8qMse3lliK$8ee1e94ab8e9f24f965083c3c083b1be23deb6713e1769f384bf6aa814f0ef7c	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:21.69212
16	Mohinur Saparova	mohinursaparova45	mohinur.saparova@gmail.com	998901112245	Artificial Intelligence	3	CS-207	pbkdf2:sha256:600000$rV6Jwvf4yoewv2uQ$616c285e1bb2a723cfd55c544cc324eeaeddbfbcdcc5b8ffa5da78802d6e607c	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:22.130141
17	Sevinch Bekchanova	sevinchbekchanova46	sevinch.bekchanova@gmail.com	998901112246	Artificial Intelligence	3	CS-207	pbkdf2:sha256:600000$4qsyfYAsMIotW831$b9dd344631bf6657970710e4d3379f7fd81a086c66739cafc8490e8b12d91c0b	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:22.596889
18	Gulnoza Yuldasheva	gulnozayuldasheva47	gulnoza.yuldasheva@gmail.com	998901112247	Artificial Intelligence	3	CS-208	pbkdf2:sha256:600000$BMaeuq3zPAjb9Ihz$3b07812e9ab751caccdbad4c35134158fdc2d9b8c6a1924f3ee6bea93cc78168	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:23.04505
19	Shaxnoza Tojimuhamedova	shaxnozatojimuhamedova48	shaxnoza.tojimuhamedova@gmail.com	998901112248	Artificial Intelligence	3	CS-208	pbkdf2:sha256:600000$SDPx68ytZleaUJRE$97e6fbaabd6f3297624963b8f49d5fc25281ffff96b2d2217468e9823c8fc0d9	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:23.511457
20	Javohir Polvonov	javohirpolvonov49	javohir.polvonov@gmail.com	998901112249	Artificial Intelligence	3	CS-209	pbkdf2:sha256:600000$JYuN8kgzWwXNPSfo$631752897f467cc8ad0481ea7a20f52ee4f3cb3466b4c73e854fe57bb30ca89f	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:23.963574
21	Umidjon Otaboyev	umidjonotaboyev50	umidjon.otaboyev@gmail.com	998901112250	Artificial Intelligence	3	CS-209	pbkdf2:sha256:600000$QIqADOzZ4ctGNJaX$6c31eef6ef79867df688036a75e2ba0ec753889ff5d1d7ed872da0f5f4e19a85	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:24.417111
22	Sardorbek Jumayev	sardorbekjumayev51	sardorbek.jumayev@gmail.com	998901112251	Artificial Intelligence	3	CS-210	pbkdf2:sha256:600000$eCiqXmOM4M5uQUfM$485f89427562183bebe52a565fab6bd4dad913beee0d30d1635114fdae249d25	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:24.86215
23	Alisher Yoqubov	alisheryoqubov52	alisher.yoqubov@gmail.com	998901112252	Artificial Intelligence	3	CS-210	pbkdf2:sha256:600000$5pFa1fVxQqDsDobF$5e60f3e1a88576a7178cfbe85cb284a30d7798f6117b86bad428c69fbc998833	user	\N	\N	f	\N	\N	f	2026-06-11 17:35:25.321908
24	Akbarjon Karimov	akbarjonkarimov01	akbarjon.karimov@gmail.com	998901234501	Data Science	2	DS-101	pbkdf2:sha256:600000$20y9zbK8WUXBP9TY$6c6166b43d3ce421fc40d800746f804f27ce6f823a7a2686df87f365f64ce926	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:50.549832
25	Bekzod Matyakubov	bekzodmatyakubov02	bekzod.matyakubov@gmail.com	998901234502	Data Science	2	DS-101	pbkdf2:sha256:600000$rQQ7mKclZZyOvT4X$df4ee89a3fbf49d75bf960159ba57bd16ae97296ce766b0f81640df02fc11d53	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:51.081879
26	Dilshod Jumaniyozov	dilshodjumaniyozov03	dilshod.jumaniyozov@gmail.com	998901234503	Data Science	2	DS-101	pbkdf2:sha256:600000$4IESjUr1NtjR7Ylq$aced19f750514b9ced24b8145b69f8453c19995a0b1380f08594331f5e77ea7d	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:51.592241
27	Jasurbek Raximov	jasurbekraximov04	jasurbek.raximov@gmail.com	998901234504	Data Science	2	DS-101	pbkdf2:sha256:600000$Cq3dO0irV5zSlvKx$3c8ec7e87114449b73b24ee83ea78df39526704b15d3740b928e4c73ab1140ed	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:52.125149
28	Muhammadali Yusupov	muhammadaliyusupov05	muhammadali.yusupov@gmail.com	998901234505	Data Science	2	DS-101	pbkdf2:sha256:600000$XAhs1q2v9BlMmcRQ$800f2c85fc2a39527e004282a7737e55ae48aa01527316c949b7e793fc118639	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:52.689365
29	Nodirbek Ergashev	nodirbekergashev06	nodirbek.ergashev@gmail.com	998901234506	Data Science	2	DS-101	pbkdf2:sha256:600000$tunnQIcmeqc911yZ$87acb2bd2ce6453a8b4a2fd17713d5f54ef7f6c88257393eccb38fd27df1926c	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:53.175901
30	Otabek Qodirov	otabekqodirov07	otabek.qodirov@gmail.com	998901234507	Data Science	2	DS-101	pbkdf2:sha256:600000$4W1I6xNvq6A92alM$ae03db0bb89eabdf4c6d6518575522196c01d00211a705935a24fec008fe1c8f	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:53.635628
31	Sardorbek Ismoilov	sardorbekismoilov08	sardorbek.ismoilov@gmail.com	998901234508	Data Science	2	DS-101	pbkdf2:sha256:600000$hO5h9gbG91XpabKP$072dd1a192c5ab176f188c566486f030fa50b61617c563691c9ca9b686e97195	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:54.0886
33	Temurbek Polvonov	temurbekpolvonov10	temurbek.polvonov@gmail.com	998901234510	Data Science	2	DS-101	pbkdf2:sha256:600000$8iKDeuBZ2lKebskh$65278798532ab64bca55b7e826ba32fa56e25f4f72018660681b467f276dfdb9	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:55.022248
34	Nilufar Karimova	nilufarkarimova12	nilufar.karimova@gmail.com	998901234512	Data Science	2	DS-101	pbkdf2:sha256:600000$mjlaknynRVUAYDAm$6ff02deca817f7d351e54e4744c7e8a75b62dd931983884048abc110b31555db	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:55.474767
35	Mohinur Bekchanova	mohinurbekchanova13	mohinur.bekchanova@gmail.com	998901234513	Data Science	2	DS-101	pbkdf2:sha256:600000$QoxTZoO2A6NQmECG$45d6c271152330082b27e2830793e7dedeb747a1f802d1b82d738a148bc60137	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:55.935919
36	Sevinch Jumayeva	sevinchjumayeva14	sevinch.jumayeva@gmail.com	998901234514	Data Science	2	DS-101	pbkdf2:sha256:600000$qkYoEFcrDcblrpbZ$a3e4cee7852f7d4c99bf71a10f830064ed1b3880f2a0e5c4653f53c12c07aff9	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:56.393876
37	Gulnoza Xudoyberdiyeva	gulnozaxudoyberdiyeva15	gulnoza.xudoyberdiyeva@gmail.com	998901234515	Data Science	2	DS-101	pbkdf2:sha256:600000$fLXS7NEtxeM456WP$d0a7b9ed6b960890c12d0b3f76695e2d2481ac9beac1d1ff120ffdf19d520ef0	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:56.84749
38	Shahnoza Tursunova	shahnozatursunova16	shahnoza.tursunova@gmail.com	998901234516	Data Science	2	DS-101	pbkdf2:sha256:600000$JznBKImqqmNNkCAQ$a8cca376cdf458b2cbba25beae45748e02a3e58e3d17e7300e9e6d2a6e1b69b6	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:57.304304
39	Madina Yoqubova	madinayoqubova17	madina.yoqubova@gmail.com	998901234517	Data Science	2	DS-101	pbkdf2:sha256:600000$TqtJuyDl9PUj5fGD$8228d43e8307360bab7b583c7e2f72d4e75335dbe0e96c7265a8c83737011833	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:57.752981
40	Zarnigor Otaboyeva	zarnigorotaboyeva18	zarnigor.otaboyeva@gmail.com	998901234518	Data Science	2	DS-101	pbkdf2:sha256:600000$V67QKGhOgt8k3t3f$7a645f885ffc4c345bab8ce7e486bf131ce55f130e66dca7702016c07a9696cc	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:58.201447
41	Dildora Matkarimova	dildoramatkarimova19	dildora.matkarimova@gmail.com	998901234519	Data Science	2	DS-101	pbkdf2:sha256:600000$nDx4yf9WhZrnZn0o$ba794df897f26a6cdce90711a19114d886952c5d7eb9a0db7b1e5238985a2b9b	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:58.664591
42	Feruza Saparova	feruzasaparova20	feruza.saparova@gmail.com	998901234520	Data Science	2	DS-101	pbkdf2:sha256:600000$PicLI735mAAIgow3$86f0b9178534fc2a4e64b74757c6439e76c7ea141677d0a344dc1dc56dffdc9c	user	\N	\N	f	\N	\N	f	2026-06-11 17:41:59.127517
32	Shohjahon Sobirov	shohjahonsobirov09	shohjahon.sobirov@gmail.com	998901234509	Data Science	2	DS-101	pbkdf2:sha256:600000$LH3EADqopXEmjhNC$6017ee5a02a28c88740feee2339b1b79255e843b2751b83a61d16b91fadd74e2	user	\N	\N	f	2026-06-11 17:43:54.388958	2026-06-11 17:43:54.388958	f	2026-06-11 17:41:54.554755
\.


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 7, true);


--
-- Name: announcements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcements_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 2, true);


--
-- Name: authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.authors_id_seq', 9, true);


--
-- Name: book_copies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.book_copies_id_seq', 54, true);


--
-- Name: book_reads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.book_reads_id_seq', 1, true);


--
-- Name: books_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.books_id_seq', 18, true);


--
-- Name: borrow_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.borrow_history_id_seq', 1, true);


--
-- Name: borrow_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.borrow_requests_id_seq', 2, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 16, true);


--
-- Name: competition_books_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competition_books_id_seq', 1, false);


--
-- Name: competition_certificates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competition_certificates_id_seq', 1, true);


--
-- Name: competition_faculties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competition_faculties_id_seq', 1, false);


--
-- Name: competition_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competition_groups_id_seq', 1, false);


--
-- Name: competition_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competition_questions_id_seq', 3, true);


--
-- Name: faculties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.faculties_id_seq', 3, true);


--
-- Name: favorite_books_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.favorite_books_id_seq', 1, false);


--
-- Name: impersonation_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.impersonation_logs_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 7, true);


--
-- Name: pdf_bookmarks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pdf_bookmarks_id_seq', 1, false);


--
-- Name: question_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.question_categories_id_seq', 1, false);


--
-- Name: quiz_attempt_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_attempt_answers_id_seq', 3, true);


--
-- Name: quiz_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_attempts_id_seq', 1, true);


--
-- Name: quiz_question_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_question_options_id_seq', 10, true);


--
-- Name: quiz_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_questions_id_seq', 3, true);


--
-- Name: quiz_violations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quiz_violations_id_seq', 1, false);


--
-- Name: reading_competitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reading_competitions_id_seq', 1, true);


--
-- Name: reading_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reading_progress_id_seq', 1, true);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_id_seq', 1, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.settings_id_seq', 1, false);


--
-- Name: site_banners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.site_banners_id_seq', 1, false);


--
-- Name: user_badges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_badges_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 42, true);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: authors authors_fullname_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_fullname_key UNIQUE (fullname);


--
-- Name: authors authors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pkey PRIMARY KEY (id);


--
-- Name: book_copies book_copies_nn_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_copies
    ADD CONSTRAINT book_copies_nn_number_key UNIQUE (nn_number);


--
-- Name: book_copies book_copies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_copies
    ADD CONSTRAINT book_copies_pkey PRIMARY KEY (id);


--
-- Name: book_reads book_reads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_reads
    ADD CONSTRAINT book_reads_pkey PRIMARY KEY (id);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);


--
-- Name: borrow_history borrow_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_history
    ADD CONSTRAINT borrow_history_pkey PRIMARY KEY (id);


--
-- Name: borrow_requests borrow_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_requests
    ADD CONSTRAINT borrow_requests_pkey PRIMARY KEY (id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: competition_books competition_books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_books
    ADD CONSTRAINT competition_books_pkey PRIMARY KEY (id);


--
-- Name: competition_certificates competition_certificates_attempt_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_attempt_id_key UNIQUE (attempt_id);


--
-- Name: competition_certificates competition_certificates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_pkey PRIMARY KEY (id);


--
-- Name: competition_certificates competition_certificates_verification_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_verification_code_key UNIQUE (verification_code);


--
-- Name: competition_faculties competition_faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_faculties
    ADD CONSTRAINT competition_faculties_pkey PRIMARY KEY (id);


--
-- Name: competition_groups competition_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_groups
    ADD CONSTRAINT competition_groups_pkey PRIMARY KEY (id);


--
-- Name: competition_questions competition_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_questions
    ADD CONSTRAINT competition_questions_pkey PRIMARY KEY (id);


--
-- Name: digital_books digital_books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_books
    ADD CONSTRAINT digital_books_pkey PRIMARY KEY (id);


--
-- Name: faculties faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_pkey PRIMARY KEY (id);


--
-- Name: favorite_books favorite_books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_books
    ADD CONSTRAINT favorite_books_pkey PRIMARY KEY (id);


--
-- Name: impersonation_logs impersonation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_logs
    ADD CONSTRAINT impersonation_logs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: pdf_bookmarks pdf_bookmarks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_bookmarks
    ADD CONSTRAINT pdf_bookmarks_pkey PRIMARY KEY (id);


--
-- Name: physical_books physical_books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.physical_books
    ADD CONSTRAINT physical_books_pkey PRIMARY KEY (id);


--
-- Name: question_categories question_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_categories
    ADD CONSTRAINT question_categories_name_key UNIQUE (name);


--
-- Name: question_categories question_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_categories
    ADD CONSTRAINT question_categories_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempt_answers quiz_attempt_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempt_answers
    ADD CONSTRAINT quiz_attempt_answers_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempts quiz_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_pkey PRIMARY KEY (id);


--
-- Name: quiz_question_options quiz_question_options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_question_options
    ADD CONSTRAINT quiz_question_options_pkey PRIMARY KEY (id);


--
-- Name: quiz_questions quiz_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_questions
    ADD CONSTRAINT quiz_questions_pkey PRIMARY KEY (id);


--
-- Name: quiz_violations quiz_violations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_violations
    ADD CONSTRAINT quiz_violations_pkey PRIMARY KEY (id);


--
-- Name: reading_competitions reading_competitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_competitions
    ADD CONSTRAINT reading_competitions_pkey PRIMARY KEY (id);


--
-- Name: reading_progress reading_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_progress
    ADD CONSTRAINT reading_progress_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: settings settings_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_key_key UNIQUE (key);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: site_banners site_banners_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_banners
    ADD CONSTRAINT site_banners_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempt_answers uq_attempt_question; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempt_answers
    ADD CONSTRAINT uq_attempt_question UNIQUE (attempt_id, question_id);


--
-- Name: book_reads uq_book_read_user_book; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_reads
    ADD CONSTRAINT uq_book_read_user_book UNIQUE (user_id, book_id);


--
-- Name: competition_books uq_competition_book; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_books
    ADD CONSTRAINT uq_competition_book UNIQUE (competition_id, book_id);


--
-- Name: competition_faculties uq_competition_faculty; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_faculties
    ADD CONSTRAINT uq_competition_faculty UNIQUE (competition_id, faculty_id);


--
-- Name: competition_groups uq_competition_group; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_groups
    ADD CONSTRAINT uq_competition_group UNIQUE (competition_id, group_name);


--
-- Name: competition_questions uq_competition_question; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_questions
    ADD CONSTRAINT uq_competition_question UNIQUE (competition_id, question_id);


--
-- Name: favorite_books uq_user_book_fav; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_books
    ADD CONSTRAINT uq_user_book_fav UNIQUE (user_id, book_id);


--
-- Name: user_badges user_badges_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT user_badges_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_activity_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_created_at ON public.activity_logs USING btree (created_at);


--
-- Name: ix_book_reads_book_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_book_reads_book_id ON public.book_reads USING btree (book_id);


--
-- Name: ix_book_reads_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_book_reads_user_id ON public.book_reads USING btree (user_id);


--
-- Name: ix_books_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_books_title ON public.books USING btree (title);


--
-- Name: ix_faculties_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_faculties_name ON public.faculties USING btree (name);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_faculty_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_faculty_id ON public.users USING btree (faculty_id);


--
-- Name: ix_users_phone_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_phone_number ON public.users USING btree (phone_number);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: audit_logs audit_logs_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: book_copies book_copies_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_copies
    ADD CONSTRAINT book_copies_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: book_reads book_reads_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_reads
    ADD CONSTRAINT book_reads_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.digital_books(id) ON DELETE CASCADE;


--
-- Name: book_reads book_reads_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_reads
    ADD CONSTRAINT book_reads_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: books books_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.authors(id);


--
-- Name: books books_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: borrow_history borrow_history_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_history
    ADD CONSTRAINT borrow_history_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: borrow_history borrow_history_copy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_history
    ADD CONSTRAINT borrow_history_copy_id_fkey FOREIGN KEY (copy_id) REFERENCES public.book_copies(id);


--
-- Name: borrow_history borrow_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_history
    ADD CONSTRAINT borrow_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: borrow_requests borrow_requests_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_requests
    ADD CONSTRAINT borrow_requests_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: borrow_requests borrow_requests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrow_requests
    ADD CONSTRAINT borrow_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: competition_books competition_books_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_books
    ADD CONSTRAINT competition_books_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: competition_books competition_books_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_books
    ADD CONSTRAINT competition_books_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: competition_certificates competition_certificates_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.quiz_attempts(id) ON DELETE CASCADE;


--
-- Name: competition_certificates competition_certificates_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: competition_certificates competition_certificates_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_certificates
    ADD CONSTRAINT competition_certificates_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: competition_faculties competition_faculties_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_faculties
    ADD CONSTRAINT competition_faculties_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: competition_faculties competition_faculties_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_faculties
    ADD CONSTRAINT competition_faculties_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id);


--
-- Name: competition_groups competition_groups_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_groups
    ADD CONSTRAINT competition_groups_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: competition_questions competition_questions_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_questions
    ADD CONSTRAINT competition_questions_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: competition_questions competition_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competition_questions
    ADD CONSTRAINT competition_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quiz_questions(id) ON DELETE CASCADE;


--
-- Name: digital_books digital_books_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_books
    ADD CONSTRAINT digital_books_id_fkey FOREIGN KEY (id) REFERENCES public.books(id);


--
-- Name: favorite_books favorite_books_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_books
    ADD CONSTRAINT favorite_books_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: favorite_books favorite_books_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_books
    ADD CONSTRAINT favorite_books_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: impersonation_logs impersonation_logs_superadmin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_logs
    ADD CONSTRAINT impersonation_logs_superadmin_id_fkey FOREIGN KEY (superadmin_id) REFERENCES public.users(id);


--
-- Name: impersonation_logs impersonation_logs_target_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_logs
    ADD CONSTRAINT impersonation_logs_target_user_id_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: pdf_bookmarks pdf_bookmarks_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_bookmarks
    ADD CONSTRAINT pdf_bookmarks_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.digital_books(id) ON DELETE CASCADE;


--
-- Name: pdf_bookmarks pdf_bookmarks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_bookmarks
    ADD CONSTRAINT pdf_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: physical_books physical_books_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.physical_books
    ADD CONSTRAINT physical_books_id_fkey FOREIGN KEY (id) REFERENCES public.books(id);


--
-- Name: quiz_attempt_answers quiz_attempt_answers_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempt_answers
    ADD CONSTRAINT quiz_attempt_answers_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.quiz_attempts(id) ON DELETE CASCADE;


--
-- Name: quiz_attempt_answers quiz_attempt_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempt_answers
    ADD CONSTRAINT quiz_attempt_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quiz_questions(id) ON DELETE CASCADE;


--
-- Name: quiz_attempts quiz_attempts_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE CASCADE;


--
-- Name: quiz_attempts quiz_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: quiz_question_options quiz_question_options_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_question_options
    ADD CONSTRAINT quiz_question_options_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quiz_questions(id) ON DELETE CASCADE;


--
-- Name: quiz_questions quiz_questions_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_questions
    ADD CONSTRAINT quiz_questions_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id) ON DELETE SET NULL;


--
-- Name: quiz_questions quiz_questions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_questions
    ADD CONSTRAINT quiz_questions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.question_categories(id) ON DELETE SET NULL;


--
-- Name: quiz_questions quiz_questions_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_questions
    ADD CONSTRAINT quiz_questions_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: quiz_violations quiz_violations_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quiz_violations
    ADD CONSTRAINT quiz_violations_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.quiz_attempts(id) ON DELETE CASCADE;


--
-- Name: reading_competitions reading_competitions_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_competitions
    ADD CONSTRAINT reading_competitions_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: reading_progress reading_progress_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_progress
    ADD CONSTRAINT reading_progress_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.digital_books(id) ON DELETE CASCADE;


--
-- Name: reading_progress reading_progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reading_progress
    ADD CONSTRAINT reading_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: reviews reviews_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: reviews reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_badges user_badges_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT user_badges_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.reading_competitions(id) ON DELETE SET NULL;


--
-- Name: user_badges user_badges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT user_badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 1pv5ovVsCkVCyOoPFDT3xJXPWvxl30GkHofYkSg6C9KwvFNxV3tyOneeWDEUqTS

