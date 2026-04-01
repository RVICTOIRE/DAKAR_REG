--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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

--
-- Name: raw_kobo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA raw_kobo;


ALTER SCHEMA raw_kobo OWNER TO postgres;

--
-- Name: SCHEMA raw_kobo; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA raw_kobo IS 'Schéma RAW : données brutes de KoboToolbox, structure exacte du formulaire';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: raw_kobo; Owner: postgres
--

CREATE FUNCTION raw_kobo.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION raw_kobo.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories_personnel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories_personnel (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.categories_personnel OWNER TO postgres;

--
-- Name: categories_personnel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_personnel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_personnel_id_seq OWNER TO postgres;

--
-- Name: categories_personnel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_personnel_id_seq OWNED BY public.categories_personnel.id;


--
-- Name: circuit_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.circuit_status (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.circuit_status OWNER TO postgres;

--
-- Name: circuit_status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.circuit_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.circuit_status_id_seq OWNER TO postgres;

--
-- Name: circuit_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.circuit_status_id_seq OWNED BY public.circuit_status.id;


--
-- Name: collection_circuits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_circuits (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    ordre integer DEFAULT 0,
    nom_circuit character varying(255),
    camion character varying(100),
    concessionnaire_id integer,
    heure_debut time without time zone,
    heure_fin time without time zone,
    duree_collecte numeric(5,2),
    poids_circuit numeric(10,2),
    status_id integer,
    observation_circuit text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT collection_circuits_poids_circuit_check CHECK ((poids_circuit >= (0)::numeric))
);


ALTER TABLE public.collection_circuits OWNER TO postgres;

--
-- Name: TABLE collection_circuits; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.collection_circuits IS 'Circuits de collecte des déchets (groupe répétitif)';


--
-- Name: collection_circuits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_circuits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_circuits_id_seq OWNER TO postgres;

--
-- Name: collection_circuits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_circuits_id_seq OWNED BY public.collection_circuits.id;


--
-- Name: concessionnaires; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.concessionnaires (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    nom character varying(255) NOT NULL,
    description text,
    actif boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.concessionnaires OWNER TO postgres;

--
-- Name: TABLE concessionnaires; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.concessionnaires IS 'Concessionnaires (opérateurs de collecte)';


--
-- Name: concessionnaires_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.concessionnaires_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.concessionnaires_id_seq OWNER TO postgres;

--
-- Name: concessionnaires_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.concessionnaires_id_seq OWNED BY public.concessionnaires.id;


--
-- Name: daily_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_reports (
    id integer NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    date_rapport date NOT NULL,
    departement_id integer NOT NULL,
    unite_communale_id integer NOT NULL,
    responsable_uc character varying(255),
    circuits_planifies integer DEFAULT 0,
    circuits_collectes integer DEFAULT 0,
    tonnage_total numeric(10,2) DEFAULT 0,
    depots_recurrents integer DEFAULT 0,
    depots_recurrents_leves integer DEFAULT 0,
    depots_sauvages integer DEFAULT 0,
    depots_sauvages_traites integer DEFAULT 0,
    sites_caisse integer DEFAULT 0,
    nb_caisses integer DEFAULT 0,
    caisses_levees integer DEFAULT 0,
    poids_caisses numeric(10,2) DEFAULT 0,
    nombre_circuits_planifies integer DEFAULT 0,
    circuits_balayage integer DEFAULT 0,
    km_planifies numeric(10,2) DEFAULT 0,
    km_balayes numeric(10,2) DEFAULT 0,
    km_desensable numeric(10,2) DEFAULT 0,
    photo_net character varying(255),
    gps_photo public.geometry(Point,4326),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    kobo_submission_id character varying(255),
    raw_submission_id integer,
    autres_difficultes text,
    autres_recommandations text,
    CONSTRAINT daily_reports_caisses_levees_check CHECK ((caisses_levees >= 0)),
    CONSTRAINT daily_reports_circuits_balayage_check CHECK ((circuits_balayage >= 0)),
    CONSTRAINT daily_reports_circuits_collectes_check CHECK ((circuits_collectes >= 0)),
    CONSTRAINT daily_reports_circuits_planifies_check CHECK ((circuits_planifies >= 0)),
    CONSTRAINT daily_reports_depots_recurrents_check CHECK ((depots_recurrents >= 0)),
    CONSTRAINT daily_reports_depots_recurrents_leves_check CHECK ((depots_recurrents_leves >= 0)),
    CONSTRAINT daily_reports_depots_sauvages_check CHECK ((depots_sauvages >= 0)),
    CONSTRAINT daily_reports_depots_sauvages_traites_check CHECK ((depots_sauvages_traites >= 0)),
    CONSTRAINT daily_reports_km_balayes_check CHECK ((km_balayes >= (0)::numeric)),
    CONSTRAINT daily_reports_km_desensable_check CHECK ((km_desensable >= (0)::numeric)),
    CONSTRAINT daily_reports_km_planifies_check CHECK ((km_planifies >= (0)::numeric)),
    CONSTRAINT daily_reports_nb_caisses_check CHECK ((nb_caisses >= 0)),
    CONSTRAINT daily_reports_nombre_circuits_planifies_check CHECK ((nombre_circuits_planifies >= 0)),
    CONSTRAINT daily_reports_poids_caisses_check CHECK ((poids_caisses >= (0)::numeric)),
    CONSTRAINT daily_reports_sites_caisse_check CHECK ((sites_caisse >= 0)),
    CONSTRAINT daily_reports_tonnage_total_check CHECK ((tonnage_total >= (0)::numeric))
);


ALTER TABLE public.daily_reports OWNER TO postgres;

--
-- Name: TABLE daily_reports; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.daily_reports IS 'Table principale des rapports journaliers de collecte des déchets';


--
-- Name: COLUMN daily_reports.gps_photo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.daily_reports.gps_photo IS 'Point GPS de la photo de nettoyage (PostGIS POINT)';


--
-- Name: daily_reports_difficultes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_reports_difficultes (
    daily_report_id integer NOT NULL,
    difficulte_id integer NOT NULL
);


ALTER TABLE public.daily_reports_difficultes OWNER TO postgres;

--
-- Name: daily_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.daily_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_reports_id_seq OWNER TO postgres;

--
-- Name: daily_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.daily_reports_id_seq OWNED BY public.daily_reports.id;


--
-- Name: daily_reports_recommandations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_reports_recommandations (
    daily_report_id integer NOT NULL,
    recommandation_id integer NOT NULL
);


ALTER TABLE public.daily_reports_recommandations OWNER TO postgres;

--
-- Name: departements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departements (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    nom character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.departements OWNER TO postgres;

--
-- Name: TABLE departements; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.departements IS 'Dictionnaire des départements';


--
-- Name: departements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departements_id_seq OWNER TO postgres;

--
-- Name: departements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departements_id_seq OWNED BY public.departements.id;


--
-- Name: difficultes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.difficultes (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.difficultes OWNER TO postgres;

--
-- Name: difficultes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.difficultes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.difficultes_id_seq OWNER TO postgres;

--
-- Name: difficultes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.difficultes_id_seq OWNED BY public.difficultes.id;


--
-- Name: interventions_ponctuelles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interventions_ponctuelles (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    ordre integer DEFAULT 0,
    agents_interv integer DEFAULT 0,
    pelles integer DEFAULT 0,
    tasseuses integer DEFAULT 0,
    camions integer DEFAULT 0,
    quartiers text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT interventions_ponctuelles_agents_interv_check CHECK ((agents_interv >= 0)),
    CONSTRAINT interventions_ponctuelles_camions_check CHECK ((camions >= 0)),
    CONSTRAINT interventions_ponctuelles_pelles_check CHECK ((pelles >= 0)),
    CONSTRAINT interventions_ponctuelles_tasseuses_check CHECK ((tasseuses >= 0))
);


ALTER TABLE public.interventions_ponctuelles OWNER TO postgres;

--
-- Name: TABLE interventions_ponctuelles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.interventions_ponctuelles IS 'Interventions ponctuelles (groupe répétitif)';


--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interventions_ponctuelles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interventions_ponctuelles_id_seq OWNER TO postgres;

--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interventions_ponctuelles_id_seq OWNED BY public.interventions_ponctuelles.id;


--
-- Name: mobilier_urbain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mobilier_urbain (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    ordre integer DEFAULT 0,
    type_mobilier_id integer,
    nb_sites integer DEFAULT 0,
    nb_bacs integer DEFAULT 0,
    bacs_leves integer DEFAULT 0,
    observation_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT mobilier_urbain_bacs_leves_check CHECK ((bacs_leves >= 0)),
    CONSTRAINT mobilier_urbain_nb_bacs_check CHECK ((nb_bacs >= 0)),
    CONSTRAINT mobilier_urbain_nb_sites_check CHECK ((nb_sites >= 0))
);


ALTER TABLE public.mobilier_urbain OWNER TO postgres;

--
-- Name: TABLE mobilier_urbain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.mobilier_urbain IS 'Mobilier urbain (groupe répétitif)';


--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mobilier_urbain_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mobilier_urbain_id_seq OWNER TO postgres;

--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mobilier_urbain_id_seq OWNED BY public.mobilier_urbain.id;


--
-- Name: observations_mobilier; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.observations_mobilier (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.observations_mobilier OWNER TO postgres;

--
-- Name: observations_mobilier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.observations_mobilier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.observations_mobilier_id_seq OWNER TO postgres;

--
-- Name: observations_mobilier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.observations_mobilier_id_seq OWNED BY public.observations_mobilier.id;


--
-- Name: personnel_apres_midi; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personnel_apres_midi (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    ordre integer DEFAULT 0,
    categorie_id integer,
    effectif_total integer DEFAULT 0,
    presents integer DEFAULT 0,
    absents integer DEFAULT 0,
    malades integer DEFAULT 0,
    conges integer DEFAULT 0,
    retard integer DEFAULT 0,
    observations text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT personnel_apres_midi_absents_check CHECK ((absents >= 0)),
    CONSTRAINT personnel_apres_midi_conges_check CHECK ((conges >= 0)),
    CONSTRAINT personnel_apres_midi_effectif_total_check CHECK ((effectif_total >= 0)),
    CONSTRAINT personnel_apres_midi_malades_check CHECK ((malades >= 0)),
    CONSTRAINT personnel_apres_midi_presents_check CHECK ((presents >= 0)),
    CONSTRAINT personnel_apres_midi_retard_check CHECK ((retard >= 0))
);


ALTER TABLE public.personnel_apres_midi OWNER TO postgres;

--
-- Name: TABLE personnel_apres_midi; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.personnel_apres_midi IS 'Personnel de l''après-midi (groupe répétitif)';


--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personnel_apres_midi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.personnel_apres_midi_id_seq OWNER TO postgres;

--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personnel_apres_midi_id_seq OWNED BY public.personnel_apres_midi.id;


--
-- Name: personnel_matin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personnel_matin (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    categorie_id integer,
    effectif_total integer DEFAULT 0,
    presents integer DEFAULT 0,
    absents integer DEFAULT 0,
    malades integer DEFAULT 0,
    retard integer DEFAULT 0,
    conges integer DEFAULT 0,
    observations text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT personnel_matin_absents_check CHECK ((absents >= 0)),
    CONSTRAINT personnel_matin_conges_check CHECK ((conges >= 0)),
    CONSTRAINT personnel_matin_effectif_total_check CHECK ((effectif_total >= 0)),
    CONSTRAINT personnel_matin_malades_check CHECK ((malades >= 0)),
    CONSTRAINT personnel_matin_presents_check CHECK ((presents >= 0)),
    CONSTRAINT personnel_matin_retard_check CHECK ((retard >= 0))
);


ALTER TABLE public.personnel_matin OWNER TO postgres;

--
-- Name: TABLE personnel_matin; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.personnel_matin IS 'Personnel du matin (groupe simple, une ligne par catégorie)';


--
-- Name: personnel_matin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personnel_matin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.personnel_matin_id_seq OWNER TO postgres;

--
-- Name: personnel_matin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personnel_matin_id_seq OWNED BY public.personnel_matin.id;


--
-- Name: personnel_nuit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personnel_nuit (
    id integer NOT NULL,
    daily_report_id integer NOT NULL,
    ordre integer DEFAULT 0,
    categorie_id integer,
    effectif_total integer DEFAULT 0,
    presents integer DEFAULT 0,
    absents integer DEFAULT 0,
    malades integer DEFAULT 0,
    conges integer DEFAULT 0,
    retard integer DEFAULT 0,
    observations text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT personnel_nuit_absents_check CHECK ((absents >= 0)),
    CONSTRAINT personnel_nuit_conges_check CHECK ((conges >= 0)),
    CONSTRAINT personnel_nuit_effectif_total_check CHECK ((effectif_total >= 0)),
    CONSTRAINT personnel_nuit_malades_check CHECK ((malades >= 0)),
    CONSTRAINT personnel_nuit_presents_check CHECK ((presents >= 0)),
    CONSTRAINT personnel_nuit_retard_check CHECK ((retard >= 0))
);


ALTER TABLE public.personnel_nuit OWNER TO postgres;

--
-- Name: TABLE personnel_nuit; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.personnel_nuit IS 'Personnel de nuit (groupe répétitif)';


--
-- Name: personnel_nuit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personnel_nuit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.personnel_nuit_id_seq OWNER TO postgres;

--
-- Name: personnel_nuit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personnel_nuit_id_seq OWNED BY public.personnel_nuit.id;


--
-- Name: photos_interventions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.photos_interventions (
    id integer NOT NULL,
    intervention_id integer NOT NULL,
    ordre integer DEFAULT 0,
    photo_int character varying(255),
    desc_int text,
    gps_int public.geometry(Point,4326),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.photos_interventions OWNER TO postgres;

--
-- Name: TABLE photos_interventions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.photos_interventions IS 'Photos des interventions (groupe répétitif dans interventions)';


--
-- Name: COLUMN photos_interventions.gps_int; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.photos_interventions.gps_int IS 'Point GPS de la photo d''intervention (PostGIS POINT)';


--
-- Name: photos_interventions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.photos_interventions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.photos_interventions_id_seq OWNER TO postgres;

--
-- Name: photos_interventions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.photos_interventions_id_seq OWNED BY public.photos_interventions.id;


--
-- Name: recommandations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recommandations (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.recommandations OWNER TO postgres;

--
-- Name: recommandations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recommandations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recommandations_id_seq OWNER TO postgres;

--
-- Name: recommandations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recommandations_id_seq OWNED BY public.recommandations.id;


--
-- Name: types_mobilier; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.types_mobilier (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    libelle character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.types_mobilier OWNER TO postgres;

--
-- Name: types_mobilier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.types_mobilier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.types_mobilier_id_seq OWNER TO postgres;

--
-- Name: types_mobilier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.types_mobilier_id_seq OWNED BY public.types_mobilier.id;


--
-- Name: unites_communales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.unites_communales (
    id integer NOT NULL,
    departement_id integer,
    code character varying(50) NOT NULL,
    nom character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.unites_communales OWNER TO postgres;

--
-- Name: TABLE unites_communales; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.unites_communales IS 'Dictionnaire des unités communales';


--
-- Name: unites_communales_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.unites_communales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.unites_communales_id_seq OWNER TO postgres;

--
-- Name: unites_communales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.unites_communales_id_seq OWNED BY public.unites_communales.id;


--
-- Name: v_collection_circuits_details; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_collection_circuits_details AS
 SELECT cc.id,
    cc.daily_report_id,
    dr.date_rapport,
    d.nom AS departement_nom,
    uc.nom AS unite_communale_nom,
    cc.ordre,
    cc.nom_circuit,
    cc.camion,
    c.nom AS concessionnaire_nom,
    c.code AS concessionnaire_code,
    cc.heure_debut,
    cc.heure_fin,
    cc.duree_collecte,
    cc.poids_circuit,
    cs.libelle AS status_libelle,
    cs.code AS status_code,
    cc.observation_circuit,
    cc.created_at
   FROM (((((public.collection_circuits cc
     JOIN public.daily_reports dr ON ((cc.daily_report_id = dr.id)))
     LEFT JOIN public.departements d ON ((dr.departement_id = d.id)))
     LEFT JOIN public.unites_communales uc ON ((dr.unite_communale_id = uc.id)))
     LEFT JOIN public.concessionnaires c ON ((cc.concessionnaire_id = c.id)))
     LEFT JOIN public.circuit_status cs ON ((cc.status_id = cs.id)));


ALTER VIEW public.v_collection_circuits_details OWNER TO postgres;

--
-- Name: v_daily_reports_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_daily_reports_summary AS
SELECT
    NULL::integer AS id,
    NULL::uuid AS uuid,
    NULL::date AS date_rapport,
    NULL::character varying(255) AS departement_nom,
    NULL::character varying(20) AS departement_code,
    NULL::character varying(255) AS unite_communale_nom,
    NULL::character varying(50) AS unite_communale_code,
    NULL::character varying(255) AS responsable_uc,
    NULL::integer AS circuits_planifies,
    NULL::integer AS circuits_collectes,
    NULL::numeric(10,2) AS tonnage_total,
    NULL::integer AS depots_recurrents,
    NULL::integer AS depots_recurrents_leves,
    NULL::integer AS depots_sauvages,
    NULL::integer AS depots_sauvages_traites,
    NULL::integer AS sites_caisse,
    NULL::integer AS nb_caisses,
    NULL::integer AS caisses_levees,
    NULL::numeric(10,2) AS poids_caisses,
    NULL::integer AS nombre_circuits_planifies,
    NULL::integer AS circuits_balayage,
    NULL::numeric(10,2) AS km_planifies,
    NULL::numeric(10,2) AS km_balayes,
    NULL::numeric(10,2) AS km_desensable,
    NULL::bigint AS nombre_categories_personnel_matin,
    NULL::bigint AS nombre_categories_personnel_apm,
    NULL::bigint AS nombre_categories_personnel_nuit,
    NULL::bigint AS nombre_circuits,
    NULL::bigint AS nombre_types_mobilier,
    NULL::bigint AS nombre_interventions,
    NULL::numeric AS poids_total_circuits,
    NULL::text AS difficultes_libelles,
    NULL::text AS autres_difficultes,
    NULL::text AS recommandations_libelles,
    NULL::text AS autres_recommandations,
    NULL::timestamp with time zone AS created_at,
    NULL::timestamp with time zone AS updated_at;


ALTER VIEW public.v_daily_reports_summary OWNER TO postgres;

--
-- Name: v_monthly_stats_by_departement; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_monthly_stats_by_departement AS
 SELECT date_trunc('month'::text, (dr.date_rapport)::timestamp with time zone) AS mois,
    d.id AS departement_id,
    d.nom AS departement_nom,
    count(DISTINCT dr.id) AS nombre_rapports,
    count(DISTINCT cc.id) AS nombre_circuits,
    COALESCE(sum(cc.poids_circuit), (0)::numeric) AS poids_total_circuits,
    COALESCE(avg(cc.poids_circuit), (0)::numeric) AS poids_moyen_par_circuit,
    COALESCE(sum(cc.duree_collecte), (0)::numeric) AS duree_totale_heures,
    COALESCE(avg(cc.duree_collecte), (0)::numeric) AS duree_moyenne_heures,
    count(DISTINCT
        CASE
            WHEN ((cs.code)::text = 'termine'::text) THEN cc.id
            ELSE NULL::integer
        END) AS circuits_termines,
    count(DISTINCT
        CASE
            WHEN ((cs.code)::text = 'non_termine'::text) THEN cc.id
            ELSE NULL::integer
        END) AS circuits_non_termines,
    count(DISTINCT
        CASE
            WHEN ((cs.code)::text = 'panne'::text) THEN cc.id
            ELSE NULL::integer
        END) AS circuits_panne,
    COALESCE(sum(dr.tonnage_total), (0)::numeric) AS tonnage_total_rapport,
    COALESCE(sum(dr.km_balayes), (0)::numeric) AS km_balayes_total
   FROM (((public.daily_reports dr
     JOIN public.departements d ON ((dr.departement_id = d.id)))
     LEFT JOIN public.collection_circuits cc ON ((dr.id = cc.daily_report_id)))
     LEFT JOIN public.circuit_status cs ON ((cc.status_id = cs.id)))
  GROUP BY (date_trunc('month'::text, (dr.date_rapport)::timestamp with time zone)), d.id, d.nom;


ALTER VIEW public.v_monthly_stats_by_departement OWNER TO postgres;

--
-- Name: circuits; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.circuits (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    ordre integer DEFAULT 0,
    circuit_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.circuits OWNER TO postgres;

--
-- Name: TABLE circuits; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.circuits IS 'Circuits de collecte (groupe répétitif)';


--
-- Name: circuits_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.circuits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.circuits_id_seq OWNER TO postgres;

--
-- Name: circuits_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.circuits_id_seq OWNED BY raw_kobo.circuits.id;


--
-- Name: form_versions; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.form_versions (
    id integer NOT NULL,
    version character varying(50) NOT NULL,
    form_id character varying(100) NOT NULL,
    deployed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.form_versions OWNER TO postgres;

--
-- Name: form_versions_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.form_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.form_versions_id_seq OWNER TO postgres;

--
-- Name: form_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.form_versions_id_seq OWNED BY raw_kobo.form_versions.id;


--
-- Name: import_errors; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.import_errors (
    id integer NOT NULL,
    submission_id integer,
    error_type character varying(100),
    error_message text,
    error_details jsonb,
    occurred_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.import_errors OWNER TO postgres;

--
-- Name: import_errors_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.import_errors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.import_errors_id_seq OWNER TO postgres;

--
-- Name: import_errors_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.import_errors_id_seq OWNED BY raw_kobo.import_errors.id;


--
-- Name: interventions_ponctuelles; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.interventions_ponctuelles (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    ordre integer DEFAULT 0,
    intervention_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.interventions_ponctuelles OWNER TO postgres;

--
-- Name: TABLE interventions_ponctuelles; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.interventions_ponctuelles IS 'Interventions ponctuelles (groupe répétitif)';


--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.interventions_ponctuelles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.interventions_ponctuelles_id_seq OWNER TO postgres;

--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.interventions_ponctuelles_id_seq OWNED BY raw_kobo.interventions_ponctuelles.id;


--
-- Name: mobilier_urbain; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.mobilier_urbain (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    ordre integer DEFAULT 0,
    mobilier_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.mobilier_urbain OWNER TO postgres;

--
-- Name: TABLE mobilier_urbain; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.mobilier_urbain IS 'Mobilier urbain (groupe répétitif)';


--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.mobilier_urbain_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.mobilier_urbain_id_seq OWNER TO postgres;

--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.mobilier_urbain_id_seq OWNED BY raw_kobo.mobilier_urbain.id;


--
-- Name: personnel_apres_midi; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.personnel_apres_midi (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    ordre integer DEFAULT 0,
    personnel_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.personnel_apres_midi OWNER TO postgres;

--
-- Name: TABLE personnel_apres_midi; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.personnel_apres_midi IS 'Personnel après-midi (groupe répétitif)';


--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.personnel_apres_midi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.personnel_apres_midi_id_seq OWNER TO postgres;

--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.personnel_apres_midi_id_seq OWNED BY raw_kobo.personnel_apres_midi.id;


--
-- Name: photos_interventions; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.photos_interventions (
    id integer NOT NULL,
    intervention_id integer NOT NULL,
    ordre integer DEFAULT 0,
    photo_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE raw_kobo.photos_interventions OWNER TO postgres;

--
-- Name: TABLE photos_interventions; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.photos_interventions IS 'Photos des interventions (groupe répétitif imbriqué)';


--
-- Name: photos_interventions_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.photos_interventions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.photos_interventions_id_seq OWNER TO postgres;

--
-- Name: photos_interventions_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.photos_interventions_id_seq OWNED BY raw_kobo.photos_interventions.id;


--
-- Name: submissions; Type: TABLE; Schema: raw_kobo; Owner: postgres
--

CREATE TABLE raw_kobo.submissions (
    id integer NOT NULL,
    kobo_submission_id character varying(255) NOT NULL,
    submission_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    form_data jsonb NOT NULL,
    form_version character varying(50),
    form_id character varying(100),
    device_id character varying(255),
    username character varying(255),
    instance_id character varying(255),
    imported_to_mart boolean DEFAULT false,
    import_error text,
    import_attempts integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    submission_data jsonb,
    transformed boolean DEFAULT false,
    transformed_at timestamp with time zone
);


ALTER TABLE raw_kobo.submissions OWNER TO postgres;

--
-- Name: TABLE submissions; Type: COMMENT; Schema: raw_kobo; Owner: postgres
--

COMMENT ON TABLE raw_kobo.submissions IS 'Table principale des soumissions brutes Kobo';


--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: raw_kobo; Owner: postgres
--

CREATE SEQUENCE raw_kobo.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE raw_kobo.submissions_id_seq OWNER TO postgres;

--
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: raw_kobo; Owner: postgres
--

ALTER SEQUENCE raw_kobo.submissions_id_seq OWNED BY raw_kobo.submissions.id;


--
-- Name: v_import_stats; Type: VIEW; Schema: raw_kobo; Owner: postgres
--

CREATE VIEW raw_kobo.v_import_stats AS
 SELECT count(*) AS total_submissions,
    count(
        CASE
            WHEN (imported_to_mart = true) THEN 1
            ELSE NULL::integer
        END) AS imported_count,
    count(
        CASE
            WHEN (imported_to_mart = false) THEN 1
            ELSE NULL::integer
        END) AS pending_count,
    count(
        CASE
            WHEN (import_error IS NOT NULL) THEN 1
            ELSE NULL::integer
        END) AS error_count,
    min(submission_date) AS oldest_submission,
    max(submission_date) AS newest_submission
   FROM raw_kobo.submissions;


ALTER VIEW raw_kobo.v_import_stats OWNER TO postgres;

--
-- Name: v_submissions_pending_import; Type: VIEW; Schema: raw_kobo; Owner: postgres
--

CREATE VIEW raw_kobo.v_submissions_pending_import AS
 SELECT id,
    kobo_submission_id,
    submission_date,
    form_version,
    imported_to_mart,
    import_error,
    import_attempts,
    created_at
   FROM raw_kobo.submissions
  WHERE (imported_to_mart = false)
  ORDER BY submission_date DESC;


ALTER VIEW raw_kobo.v_submissions_pending_import OWNER TO postgres;

--
-- Name: categories_personnel id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories_personnel ALTER COLUMN id SET DEFAULT nextval('public.categories_personnel_id_seq'::regclass);


--
-- Name: circuit_status id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_status ALTER COLUMN id SET DEFAULT nextval('public.circuit_status_id_seq'::regclass);


--
-- Name: collection_circuits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_circuits ALTER COLUMN id SET DEFAULT nextval('public.collection_circuits_id_seq'::regclass);


--
-- Name: concessionnaires id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concessionnaires ALTER COLUMN id SET DEFAULT nextval('public.concessionnaires_id_seq'::regclass);


--
-- Name: daily_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports ALTER COLUMN id SET DEFAULT nextval('public.daily_reports_id_seq'::regclass);


--
-- Name: departements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departements ALTER COLUMN id SET DEFAULT nextval('public.departements_id_seq'::regclass);


--
-- Name: difficultes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficultes ALTER COLUMN id SET DEFAULT nextval('public.difficultes_id_seq'::regclass);


--
-- Name: interventions_ponctuelles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions_ponctuelles ALTER COLUMN id SET DEFAULT nextval('public.interventions_ponctuelles_id_seq'::regclass);


--
-- Name: mobilier_urbain id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobilier_urbain ALTER COLUMN id SET DEFAULT nextval('public.mobilier_urbain_id_seq'::regclass);


--
-- Name: observations_mobilier id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.observations_mobilier ALTER COLUMN id SET DEFAULT nextval('public.observations_mobilier_id_seq'::regclass);


--
-- Name: personnel_apres_midi id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_apres_midi ALTER COLUMN id SET DEFAULT nextval('public.personnel_apres_midi_id_seq'::regclass);


--
-- Name: personnel_matin id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_matin ALTER COLUMN id SET DEFAULT nextval('public.personnel_matin_id_seq'::regclass);


--
-- Name: personnel_nuit id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_nuit ALTER COLUMN id SET DEFAULT nextval('public.personnel_nuit_id_seq'::regclass);


--
-- Name: photos_interventions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos_interventions ALTER COLUMN id SET DEFAULT nextval('public.photos_interventions_id_seq'::regclass);


--
-- Name: recommandations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommandations ALTER COLUMN id SET DEFAULT nextval('public.recommandations_id_seq'::regclass);


--
-- Name: types_mobilier id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.types_mobilier ALTER COLUMN id SET DEFAULT nextval('public.types_mobilier_id_seq'::regclass);


--
-- Name: unites_communales id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.unites_communales ALTER COLUMN id SET DEFAULT nextval('public.unites_communales_id_seq'::regclass);


--
-- Name: circuits id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.circuits ALTER COLUMN id SET DEFAULT nextval('raw_kobo.circuits_id_seq'::regclass);


--
-- Name: form_versions id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.form_versions ALTER COLUMN id SET DEFAULT nextval('raw_kobo.form_versions_id_seq'::regclass);


--
-- Name: import_errors id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.import_errors ALTER COLUMN id SET DEFAULT nextval('raw_kobo.import_errors_id_seq'::regclass);


--
-- Name: interventions_ponctuelles id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.interventions_ponctuelles ALTER COLUMN id SET DEFAULT nextval('raw_kobo.interventions_ponctuelles_id_seq'::regclass);


--
-- Name: mobilier_urbain id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.mobilier_urbain ALTER COLUMN id SET DEFAULT nextval('raw_kobo.mobilier_urbain_id_seq'::regclass);


--
-- Name: personnel_apres_midi id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.personnel_apres_midi ALTER COLUMN id SET DEFAULT nextval('raw_kobo.personnel_apres_midi_id_seq'::regclass);


--
-- Name: photos_interventions id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.photos_interventions ALTER COLUMN id SET DEFAULT nextval('raw_kobo.photos_interventions_id_seq'::regclass);


--
-- Name: submissions id; Type: DEFAULT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.submissions ALTER COLUMN id SET DEFAULT nextval('raw_kobo.submissions_id_seq'::regclass);


--
-- Data for Name: categories_personnel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories_personnel (id, code, libelle, created_at) FROM stdin;
1	collecteur	Collecteurs	2026-01-14 11:23:58.426974+00
2	balayeur	Balayeurs	2026-01-14 11:23:58.426974+00
3	aps	AP de site	2026-01-14 11:23:58.426974+00
4	apm	AP mobile urbain	2026-01-14 11:23:58.426974+00
5	superviseur	Superviseur	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: circuit_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.circuit_status (id, code, libelle, created_at) FROM stdin;
1	termine	Circuit terminé	2026-01-14 11:23:58.426974+00
2	non_termine	Circuit non terminé	2026-01-14 11:23:58.426974+00
3	panne	Panne	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: collection_circuits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collection_circuits (id, daily_report_id, ordre, nom_circuit, camion, concessionnaire_id, heure_debut, heure_fin, duree_collecte, poids_circuit, status_id, observation_circuit, created_at, updated_at) FROM stdin;
9	7	1	Ecotra grandes artères Matin	9061A	1	08:00:00	12:30:00	4.50	11.70	1	\N	2026-01-16 13:03:06.856147+00	2026-01-16 13:03:06.856147+00
10	7	2	Keur Khadim Medina 1A	1704	2	08:00:00	13:30:00	5.50	9920.00	1	\N	2026-01-16 13:03:06.856147+00	2026-01-16 13:03:06.856147+00
11	7	3	Delta Medina 1B	202	3	09:00:00	13:00:00	4.00	5560.00	2	\N	2026-01-16 13:03:06.856147+00	2026-01-16 13:03:06.856147+00
12	8	1	Bongre	3015	3	10:41:00	14:42:00	4.02	5823.00	2	\N	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: concessionnaires; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.concessionnaires (id, code, nom, description, actif, created_at, updated_at) FROM stdin;
1	ecotra	Ecotra	\N	t	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
2	cdf	CDF	\N	t	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
3	keur_khadim	Keur Khadim	\N	t	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: daily_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_reports (id, uuid, date_rapport, departement_id, unite_communale_id, responsable_uc, circuits_planifies, circuits_collectes, tonnage_total, depots_recurrents, depots_recurrents_leves, depots_sauvages, depots_sauvages_traites, sites_caisse, nb_caisses, caisses_levees, poids_caisses, nombre_circuits_planifies, circuits_balayage, km_planifies, km_balayes, km_desensable, photo_net, gps_photo, created_at, updated_at, created_by, kobo_submission_id, raw_submission_id, autres_difficultes, autres_recommandations) FROM stdin;
7	029421f0-cac1-41a8-90f3-898841d1b8cd	2026-01-13	1	3	\N	9	7	42.86	0	0	0	0	0	0	0	0.00	0	0	0.00	0.00	0.00	\N	\N	2026-01-16 13:03:06.856147+00	2026-01-16 13:03:06.856147+00	\N	647866117	\N	\N	\N
8	2a7287fa-3f46-4adc-9786-2330a81d48d4	2026-02-24	2	16	\N	12	10	4500.00	12	8	2	2	45	80	75	10500.00	4	4	25.00	20.00	5.00	\N	\N	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00	\N	678880762	\N	\N	\N
\.


--
-- Data for Name: daily_reports_difficultes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_reports_difficultes (daily_report_id, difficulte_id) FROM stdin;
8	1
\.


--
-- Data for Name: daily_reports_recommandations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_reports_recommandations (daily_report_id, recommandation_id) FROM stdin;
8	1
\.


--
-- Data for Name: departements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departements (id, code, nom, created_at, updated_at) FROM stdin;
1	dakar	Dakar	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
2	guediawaye	Guediawaye	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
3	pikine	Pikine	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
4	rufisque	Rufisque	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
5	keur_massar	Keur Massar	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: difficultes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.difficultes (id, code, libelle, created_at) FROM stdin;
1	materiel	Manque de matériel	2026-01-14 11:23:58.426974+00
2	effectif	Manque d'effectif	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: interventions_ponctuelles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interventions_ponctuelles (id, daily_report_id, ordre, agents_interv, pelles, tasseuses, camions, quartiers, created_at, updated_at) FROM stdin;
1	8	1	58	1	1	1	Kasnack 	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: mobilier_urbain; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mobilier_urbain (id, daily_report_id, ordre, type_mobilier_id, nb_sites, nb_bacs, bacs_leves, observation_id, created_at, updated_at) FROM stdin;
1	8	1	1	8	32	32	1	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
2	8	2	2	22	44	22	1	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
3	8	3	3	90	145	145	1	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: observations_mobilier; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.observations_mobilier (id, code, libelle, created_at) FROM stdin;
1	lev_s	Levés	2026-01-14 11:23:58.426974+00
2	pas_lev_s	Pas Levés	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: personnel_apres_midi; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personnel_apres_midi (id, daily_report_id, ordre, categorie_id, effectif_total, presents, absents, malades, conges, retard, observations, created_at, updated_at) FROM stdin;
3	7	0	1	22	0	0	0	3	6	\N	2026-01-16 13:03:06.856147+00	2026-01-16 13:03:06.856147+00
4	8	1	2	21	21	0	1	0	0	\N	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
5	8	2	5	1	1	0	0	0	0	\N	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: personnel_matin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personnel_matin (id, daily_report_id, categorie_id, effectif_total, presents, absents, malades, retard, conges, observations, created_at, updated_at) FROM stdin;
1	8	1	20	12	10	1	1	0	\N	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: personnel_nuit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personnel_nuit (id, daily_report_id, ordre, categorie_id, effectif_total, presents, absents, malades, conges, retard, observations, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: photos_interventions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.photos_interventions (id, intervention_id, ordre, photo_int, desc_int, gps_int, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: recommandations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recommandations (id, code, libelle, created_at) FROM stdin;
1	renfort	Renforcer le personnel	2026-01-14 11:23:58.426974+00
2	epi	Dotation en EPI	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: types_mobilier; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.types_mobilier (id, code, libelle, created_at) FROM stdin;
1	prn	PRN	2026-01-14 11:23:58.426974+00
2	pp	PP	2026-01-14 11:23:58.426974+00
3	bacs	Bacs de rue	2026-01-14 11:23:58.426974+00
\.


--
-- Data for Name: unites_communales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.unites_communales (id, departement_id, code, nom, created_at, updated_at) FROM stdin;
1	1	medina	Yoff	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
2	1	ngor	Ngor	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
3	1	m_dina_jour	Médina jour	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
4	1	m_dina_nuit	Médina nuit	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
5	1	mermoz_sacr__coeur	Mermoz sacré coeur	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
6	1	grand_dakar	Grand Dakar	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
7	1	biscuiterie	Biscuiterie	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
8	1	dieuppeul_derkl	Dieuppeul Derklé	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
9	1	sicap_liberte	Sicap Liberté	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
10	1	hann_bel_air	Hann bel-air	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
11	1	face_colobane_gueule_tap_e	Face-colobane-Gueule Tapée	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
12	1	plateau_jour	Plateau jour	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
13	1	plateau_nuit	Plateau nuit	2026-01-14 11:23:58.426974+00	2026-01-14 11:23:58.426974+00
16	2	guediawaye_default	Guediawaye	2026-02-24 10:58:31.251699+00	2026-02-24 10:58:31.251699+00
\.


--
-- Data for Name: circuits; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.circuits (id, submission_id, ordre, circuit_data, created_at) FROM stdin;
\.


--
-- Data for Name: form_versions; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.form_versions (id, version, form_id, deployed_at, description, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: import_errors; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.import_errors (id, submission_id, error_type, error_message, error_details, occurred_at) FROM stdin;
1	\N	NotNullViolation	ERREUR:  une valeur NULL viole la contrainte NOT NULL de la colonne « kobo_submission_id » dans la relation « submissions »\nDETAIL:  La ligne en échec contient (1, null, 2026-01-14 11:51:56.529062+00, {"_id": null, "Date du rapport;\\"Département\\";\\"Unités commun..., null, null, null, null, null, f, null, 0, 2026-01-14 11:51:56.529281+00, 2026-01-14 11:51:56.529281+00).\n	{"submission": null}	2026-01-14 11:51:56.53908+00
\.


--
-- Data for Name: interventions_ponctuelles; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.interventions_ponctuelles (id, submission_id, ordre, intervention_data, created_at) FROM stdin;
\.


--
-- Data for Name: mobilier_urbain; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.mobilier_urbain (id, submission_id, ordre, mobilier_data, created_at) FROM stdin;
\.


--
-- Data for Name: personnel_apres_midi; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.personnel_apres_midi (id, submission_id, ordre, personnel_data, created_at) FROM stdin;
\.


--
-- Data for Name: photos_interventions; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.photos_interventions (id, intervention_id, ordre, photo_data, created_at) FROM stdin;
\.


--
-- Data for Name: submissions; Type: TABLE DATA; Schema: raw_kobo; Owner: postgres
--

COPY raw_kobo.submissions (id, kobo_submission_id, submission_date, form_data, form_version, form_id, device_id, username, instance_id, imported_to_mart, import_error, import_attempts, created_at, updated_at, submission_data, transformed, transformed_at) FROM stdin;
3	647866117	2026-01-15 11:58:28.994159+00	{"_id": 647866117, "_tags": [], "_uuid": "9ba96cd0-2c96-42b7-9279-1794cbf76be3", "_notes": [], "_status": "submitted_via_web", "circuits": [{"circuits/camion": "9061A", "circuits/statut": "termine", "circuits/heure_fin": "12:30:00.000Z", "circuits/operateur": "ecotra", "circuits/heure_debut": "08:00:00.000Z", "circuits/nom_circuit": "Ecotra grandes artères Matin", "circuits/DureeCollecte": "4.5", "circuits/poids_circuit": "11.7"}, {"circuits/camion": "1704", "circuits/statut": "termine", "circuits/heure_fin": "13:30:00.000Z", "circuits/operateur": "cdf", "circuits/heure_debut": "08:00:00.000Z", "circuits/nom_circuit": "Keur Khadim Medina 1A", "circuits/DureeCollecte": "5.5", "circuits/poids_circuit": "9920.0"}, {"circuits/camion": "202", "circuits/statut": "non_termine", "circuits/heure_fin": "13:00:00.000Z", "circuits/operateur": "keur_khadim", "circuits/heure_debut": "09:00:00.000Z", "circuits/nom_circuit": "Delta Medina 1B", "circuits/DureeCollecte": "4", "circuits/poids_circuit": "5560.0"}], "mobilier": [{"mobilier/nb_bacs": "19", "mobilier/nb_sites": "4", "mobilier/bacs_leves": "19", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "prn"}, {"mobilier/nb_bacs": "19", "mobilier/nb_sites": "4", "mobilier/bacs_leves": "19", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "pp"}, {"mobilier/nb_bacs": "42", "mobilier/nb_sites": "8", "mobilier/bacs_leves": "42", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "bacs"}], "__version__": "vZ4hdwVAKpVGCK62LsSGu8", "_attachments": [], "_geolocation": [null, null], "formhub/uuid": "12450a96e9c64b96933016b852f7d0f8", "_submitted_by": null, "group_vs5fg16": [{"group_vs5fg16/pelles": "0", "group_vs5fg16/camions": "0", "group_vs5fg16/quartiers": "0", "group_vs5fg16/tasseuses": "0", "group_vs5fg16/agents_interv": "0"}], "meta/rootUuid": "uuid:9ba96cd0-2c96-42b7-9279-1794cbf76be3", "personnel_apm": [{"personnel_apm/present_apm": "10", "personnel_apm/conge_apm_001": "0", "personnel_apm/reserve_apm_002": "2", "personnel_apm/effectif_apm_001": "12", "personnel_apm/categorie_apm_002": "balayeur", "personnel_apm/absent_apm_001_001": "0", "personnel_apm/malade_apm_001_001": "0"}, {"personnel_apm/present_apm": "1", "personnel_apm/conge_apm_001": "0", "personnel_apm/reserve_apm_002": "2", "personnel_apm/effectif_apm_001": "3", "personnel_apm/categorie_apm_002": "aps", "personnel_apm/absent_apm_001_001": "0", "personnel_apm/malade_apm_001_001": "0"}, {"personnel_apm/present_apm": "3", "personnel_apm/conge_apm_001": "0", "personnel_apm/reserve_apm_002": "2", "personnel_apm/effectif_apm_001": "5", "personnel_apm/categorie_apm_002": "apm", "personnel_apm/absent_apm_001_001": "0", "personnel_apm/malade_apm_001_001": "0"}, {"personnel_apm/present_apm": "1", "personnel_apm/conge_apm_001": "0", "personnel_apm/reserve_apm_002": "0", "personnel_apm/effectif_apm_001": "1", "personnel_apm/categorie_apm_002": "superviseur", "personnel_apm/absent_apm_001_001": "0", "personnel_apm/malade_apm_001_001": "0", "personnel_apm/observation_personnel_002": "Permi les surveillants de dépôts 9 avaient été affectés au balayage mais ils pas pas balayer parcequils sont invalides"}], "meta/instanceID": "uuid:9ba96cd0-2c96-42b7-9279-1794cbf76be3", "_submission_time": "2026-01-13T14:25:29", "_xform_id_string": "aAKLQa7aKQuJZ6wANBa3iM", "_validation_status": {}, "group_nu8sp57/unite": "m_dina_jour", "group_rr8mq19/conge_apm": "3", "group_or03u90/km_balayes": "0.0", "group_rr8mq19/absent_apm": "0", "group_rr8mq19/malade_apm": "0", "group_wl43a78/nb_caisses": "0", "group_nu8sp57/D_partement": "dakar", "group_rr8mq19/reserve_apm": "6", "group_wi6jl55/difficultes": "materiel effectif", "group_nu8sp57/date_rapport": "2026-01-13", "group_or03u90/km_planifies": "0.0", "group_rr8mq19/effectif_apm": "22", "group_wl43a78/sites_caisse": "0", "group_eu7tr68/tonnage_total": "42.86", "group_or03u90/km_desensable": "0.0", "group_wl43a78/poids_caisses": "0.0", "group_nu8sp57/responsable_uc": "Omar", "group_wl43a78/caisses_levees": "0", "group_eu7tr68/depots_sauvages": "0", "group_rr8mq19/present_apm_001": "12", "group_wi6jl55/recommandations": "renfort epi", "group_eu7tr68/depots_recurrents": "6", "group_or03u90/circuits_balayage": "1", "group_rr8mq19/categorie_apm_001": "collecteur", "group_eu7tr68/circuits_collectes": "7", "group_eu7tr68/circuits_planifies": "9", "group_eu7tr68/depots_recurrents_leves": "6", "group_eu7tr68/depots_sauvages_traites": "0", "group_or03u90/Nombre_de_circuits_planifi_s": "1"}	\N	aAKLQa7aKQuJZ6wANBa3iM	\N	\N	9ba96cd0-2c96-42b7-9279-1794cbf76be3	f	ERREUR:  une valeur NULL viole la contrainte NOT NULL de la colonne « departement_id » dans la relation « daily_reports »\nDETAIL:  La ligne en échec contient (2, 784d1678-3275-4a62-b16e-72e84c3a73aa, 2026-01-13, null, null, null, 0, 0, 0.00, 0, 0, 0, 0, 0, 0, 0, 0.00, 0, 0, 0.00, 0.00, 0.00, null, null, 2026-01-16 09:46:33.79687+00, 2026-01-16 09:46:33.79687+00, null, 647866117, 3, null, null).\n	6	2026-01-15 11:58:28.994159+00	2026-01-16 13:03:06.856147+00	\N	t	2026-01-16 13:03:06.856147+00
6	678880762	2026-02-24 10:54:57.577959+00	{"_id": 678880762, "_tags": [], "_uuid": "383579af-16e9-4503-b2ae-fda6ab51da74", "_notes": [], "_status": "submitted_via_web", "circuits": [{"circuits/camion": "3015", "circuits/statut": "non_termine", "circuits/heure_fin": "14:42:00.000Z", "circuits/operateur": "keur_khadim", "circuits/heure_debut": "10:41:00.000Z", "circuits/nom_circuit": "Bongre", "circuits/DureeCollecte": "4.02", "circuits/poids_circuit": "5823.0"}], "mobilier": [{"mobilier/nb_bacs": "32", "mobilier/nb_sites": "8", "mobilier/bacs_leves": "32", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "prn"}, {"mobilier/nb_bacs": "44", "mobilier/nb_sites": "22", "mobilier/bacs_leves": "22", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "pp"}, {"mobilier/nb_bacs": "145", "mobilier/nb_sites": "90", "mobilier/bacs_leves": "145", "mobilier/Observation": "lev_s", "mobilier/type_mobilier": "bacs"}], "__version__": "vZ4hdwVAKpVGCK62LsSGu8", "_attachments": [{"uid": "atteNycq5GB8pnstsVnFfKWu", "filename": "rabyvictoire2025/attachments/12450a96e9c64b96933016b852f7d0f8/383579af-16e9-4503-b2ae-fda6ab51da74/1771929973582.jpg", "mimetype": "image/jpeg", "is_deleted": false, "download_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atteNycq5GB8pnstsVnFfKWu/", "question_xpath": "group_vs5fg16[1]/photos_interv[1]/photo_int", "download_large_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atteNycq5GB8pnstsVnFfKWu/large/", "download_small_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atteNycq5GB8pnstsVnFfKWu/small/", "download_medium_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atteNycq5GB8pnstsVnFfKWu/medium/", "media_file_basename": "1771929973582.jpg"}, {"uid": "atto6yV2puTQCqfLgT8UMvrn", "filename": "rabyvictoire2025/attachments/12450a96e9c64b96933016b852f7d0f8/383579af-16e9-4503-b2ae-fda6ab51da74/1771929800406.jpg", "mimetype": "image/jpeg", "is_deleted": false, "download_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atto6yV2puTQCqfLgT8UMvrn/", "question_xpath": "group_or03u90/photo_net", "download_large_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atto6yV2puTQCqfLgT8UMvrn/large/", "download_small_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atto6yV2puTQCqfLgT8UMvrn/small/", "download_medium_url": "https://kf.kobotoolbox.org/api/v2/assets/aAKLQa7aKQuJZ6wANBa3iM/data/678880762/attachments/atto6yV2puTQCqfLgT8UMvrn/medium/", "media_file_basename": "1771929800406.jpg"}], "_geolocation": [14.1410412, -16.0863501], "formhub/uuid": "12450a96e9c64b96933016b852f7d0f8", "_submitted_by": null, "group_rr8mq19": [{"group_rr8mq19/conge_apm": "0", "group_rr8mq19/absent_apm": "10", "group_rr8mq19/malade_apm": "1", "group_rr8mq19/reserve_apm": "1", "group_rr8mq19/effectif_apm": "20", "group_rr8mq19/present_apm_001": "12", "group_rr8mq19/categorie_apm_001": "collecteur"}], "group_vs5fg16": [{"group_vs5fg16/pelles": "1", "group_vs5fg16/camions": "1", "group_vs5fg16/quartiers": "Kasnack ", "group_vs5fg16/tasseuses": "1", "group_vs5fg16/agents_interv": "58", "group_vs5fg16/photos_interv": [{"group_vs5fg16/photos_interv/gps_int": "14.1409694 -16.086293 37.599998474121094 20.0", "group_vs5fg16/photos_interv/photo_int": "1771929973582.jpg"}]}], "meta/rootUuid": "uuid:383579af-16e9-4503-b2ae-fda6ab51da74", "personnel_apm": [{"personnel_apm/present_apm": "21", "personnel_apm/conge_apm_001": "0", "personnel_apm/reserve_apm_002": "0", "personnel_apm/effectif_apm_001": "21", "personnel_apm/categorie_apm_002": "balayeur", "personnel_apm/absent_apm_001_001": "0", "personnel_apm/malade_apm_001_001": "1"}, {"personnel_apm/present_apm": "1", "personnel_apm/effectif_apm_001": "1", "personnel_apm/categorie_apm_002": "superviseur"}], "meta/instanceID": "uuid:383579af-16e9-4503-b2ae-fda6ab51da74", "_submission_time": "2026-02-24T10:46:57", "_xform_id_string": "aAKLQa7aKQuJZ6wANBa3iM", "_validation_status": {}, "group_or03u90/gps_photo": "14.1410412 -16.0863501 37.599998474121094 5.2", "group_or03u90/photo_net": "1771929800406.jpg", "group_or03u90/km_balayes": "20.0", "group_wl43a78/nb_caisses": "80", "group_nu8sp57/D_partement": "guediawaye", "group_wi6jl55/difficultes": "materiel", "group_nu8sp57/date_rapport": "2026-02-24", "group_or03u90/km_planifies": "25.0", "group_wl43a78/sites_caisse": "45", "group_eu7tr68/tonnage_total": "4500.0", "group_or03u90/km_desensable": "5.0", "group_wl43a78/poids_caisses": "10500.0", "group_nu8sp57/responsable_uc": "M K", "group_wl43a78/caisses_levees": "75", "group_eu7tr68/depots_sauvages": "2", "group_wi6jl55/recommandations": "renfort", "group_eu7tr68/depots_recurrents": "12", "group_or03u90/circuits_balayage": "4", "group_eu7tr68/circuits_collectes": "10", "group_eu7tr68/circuits_planifies": "12", "group_eu7tr68/depots_recurrents_leves": "8", "group_eu7tr68/depots_sauvages_traites": "2", "group_or03u90/Nombre_de_circuits_planifi_s": "4"}	\N	\N	\N	\N	\N	f	\N	0	2026-02-24 10:54:57.577959+00	2026-02-24 10:58:31.251699+00	\N	t	2026-02-24 10:58:31.251699+00
\.


--
-- Name: categories_personnel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_personnel_id_seq', 5, true);


--
-- Name: circuit_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.circuit_status_id_seq', 3, true);


--
-- Name: collection_circuits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_circuits_id_seq', 12, true);


--
-- Name: concessionnaires_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.concessionnaires_id_seq', 3, true);


--
-- Name: daily_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_reports_id_seq', 8, true);


--
-- Name: departements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departements_id_seq', 5, true);


--
-- Name: difficultes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.difficultes_id_seq', 2, true);


--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interventions_ponctuelles_id_seq', 1, true);


--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mobilier_urbain_id_seq', 3, true);


--
-- Name: observations_mobilier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.observations_mobilier_id_seq', 2, true);


--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personnel_apres_midi_id_seq', 5, true);


--
-- Name: personnel_matin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personnel_matin_id_seq', 1, true);


--
-- Name: personnel_nuit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personnel_nuit_id_seq', 1, false);


--
-- Name: photos_interventions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.photos_interventions_id_seq', 1, false);


--
-- Name: recommandations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recommandations_id_seq', 2, true);


--
-- Name: types_mobilier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.types_mobilier_id_seq', 3, true);


--
-- Name: unites_communales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.unites_communales_id_seq', 16, true);


--
-- Name: circuits_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.circuits_id_seq', 1, false);


--
-- Name: form_versions_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.form_versions_id_seq', 1, false);


--
-- Name: import_errors_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.import_errors_id_seq', 1, true);


--
-- Name: interventions_ponctuelles_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.interventions_ponctuelles_id_seq', 1, false);


--
-- Name: mobilier_urbain_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.mobilier_urbain_id_seq', 1, false);


--
-- Name: personnel_apres_midi_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.personnel_apres_midi_id_seq', 1, false);


--
-- Name: photos_interventions_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.photos_interventions_id_seq', 1, false);


--
-- Name: submissions_id_seq; Type: SEQUENCE SET; Schema: raw_kobo; Owner: postgres
--

SELECT pg_catalog.setval('raw_kobo.submissions_id_seq', 6, true);


--
-- Name: categories_personnel categories_personnel_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories_personnel
    ADD CONSTRAINT categories_personnel_code_key UNIQUE (code);


--
-- Name: categories_personnel categories_personnel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories_personnel
    ADD CONSTRAINT categories_personnel_pkey PRIMARY KEY (id);


--
-- Name: circuit_status circuit_status_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_status
    ADD CONSTRAINT circuit_status_code_key UNIQUE (code);


--
-- Name: circuit_status circuit_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_status
    ADD CONSTRAINT circuit_status_pkey PRIMARY KEY (id);


--
-- Name: collection_circuits collection_circuits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_circuits
    ADD CONSTRAINT collection_circuits_pkey PRIMARY KEY (id);


--
-- Name: concessionnaires concessionnaires_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concessionnaires
    ADD CONSTRAINT concessionnaires_code_key UNIQUE (code);


--
-- Name: concessionnaires concessionnaires_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concessionnaires
    ADD CONSTRAINT concessionnaires_pkey PRIMARY KEY (id);


--
-- Name: daily_reports daily_reports_date_rapport_unite_communale_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_date_rapport_unite_communale_id_key UNIQUE (date_rapport, unite_communale_id);


--
-- Name: daily_reports_difficultes daily_reports_difficultes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_difficultes
    ADD CONSTRAINT daily_reports_difficultes_pkey PRIMARY KEY (daily_report_id, difficulte_id);


--
-- Name: daily_reports daily_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_pkey PRIMARY KEY (id);


--
-- Name: daily_reports_recommandations daily_reports_recommandations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_recommandations
    ADD CONSTRAINT daily_reports_recommandations_pkey PRIMARY KEY (daily_report_id, recommandation_id);


--
-- Name: daily_reports daily_reports_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_uuid_key UNIQUE (uuid);


--
-- Name: departements departements_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departements
    ADD CONSTRAINT departements_code_key UNIQUE (code);


--
-- Name: departements departements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departements
    ADD CONSTRAINT departements_pkey PRIMARY KEY (id);


--
-- Name: difficultes difficultes_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficultes
    ADD CONSTRAINT difficultes_code_key UNIQUE (code);


--
-- Name: difficultes difficultes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficultes
    ADD CONSTRAINT difficultes_pkey PRIMARY KEY (id);


--
-- Name: interventions_ponctuelles interventions_ponctuelles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions_ponctuelles
    ADD CONSTRAINT interventions_ponctuelles_pkey PRIMARY KEY (id);


--
-- Name: mobilier_urbain mobilier_urbain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_pkey PRIMARY KEY (id);


--
-- Name: observations_mobilier observations_mobilier_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.observations_mobilier
    ADD CONSTRAINT observations_mobilier_code_key UNIQUE (code);


--
-- Name: observations_mobilier observations_mobilier_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.observations_mobilier
    ADD CONSTRAINT observations_mobilier_pkey PRIMARY KEY (id);


--
-- Name: personnel_apres_midi personnel_apres_midi_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_apres_midi
    ADD CONSTRAINT personnel_apres_midi_pkey PRIMARY KEY (id);


--
-- Name: personnel_matin personnel_matin_daily_report_id_categorie_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_matin
    ADD CONSTRAINT personnel_matin_daily_report_id_categorie_id_key UNIQUE (daily_report_id, categorie_id);


--
-- Name: personnel_matin personnel_matin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_matin
    ADD CONSTRAINT personnel_matin_pkey PRIMARY KEY (id);


--
-- Name: personnel_nuit personnel_nuit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_nuit
    ADD CONSTRAINT personnel_nuit_pkey PRIMARY KEY (id);


--
-- Name: photos_interventions photos_interventions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos_interventions
    ADD CONSTRAINT photos_interventions_pkey PRIMARY KEY (id);


--
-- Name: recommandations recommandations_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommandations
    ADD CONSTRAINT recommandations_code_key UNIQUE (code);


--
-- Name: recommandations recommandations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommandations
    ADD CONSTRAINT recommandations_pkey PRIMARY KEY (id);


--
-- Name: types_mobilier types_mobilier_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.types_mobilier
    ADD CONSTRAINT types_mobilier_code_key UNIQUE (code);


--
-- Name: types_mobilier types_mobilier_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.types_mobilier
    ADD CONSTRAINT types_mobilier_pkey PRIMARY KEY (id);


--
-- Name: unites_communales unites_communales_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.unites_communales
    ADD CONSTRAINT unites_communales_code_key UNIQUE (code);


--
-- Name: unites_communales unites_communales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.unites_communales
    ADD CONSTRAINT unites_communales_pkey PRIMARY KEY (id);


--
-- Name: circuits circuits_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.circuits
    ADD CONSTRAINT circuits_pkey PRIMARY KEY (id);


--
-- Name: form_versions form_versions_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.form_versions
    ADD CONSTRAINT form_versions_pkey PRIMARY KEY (id);


--
-- Name: form_versions form_versions_version_key; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.form_versions
    ADD CONSTRAINT form_versions_version_key UNIQUE (version);


--
-- Name: import_errors import_errors_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.import_errors
    ADD CONSTRAINT import_errors_pkey PRIMARY KEY (id);


--
-- Name: interventions_ponctuelles interventions_ponctuelles_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.interventions_ponctuelles
    ADD CONSTRAINT interventions_ponctuelles_pkey PRIMARY KEY (id);


--
-- Name: mobilier_urbain mobilier_urbain_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_pkey PRIMARY KEY (id);


--
-- Name: personnel_apres_midi personnel_apres_midi_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.personnel_apres_midi
    ADD CONSTRAINT personnel_apres_midi_pkey PRIMARY KEY (id);


--
-- Name: photos_interventions photos_interventions_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.photos_interventions
    ADD CONSTRAINT photos_interventions_pkey PRIMARY KEY (id);


--
-- Name: submissions submissions_kobo_submission_id_key; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.submissions
    ADD CONSTRAINT submissions_kobo_submission_id_key UNIQUE (kobo_submission_id);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: idx_collection_circuits_concessionnaire; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_circuits_concessionnaire ON public.collection_circuits USING btree (concessionnaire_id);


--
-- Name: idx_collection_circuits_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_circuits_report ON public.collection_circuits USING btree (daily_report_id);


--
-- Name: idx_collection_circuits_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_circuits_status ON public.collection_circuits USING btree (status_id);


--
-- Name: idx_daily_reports_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_reports_created_at ON public.daily_reports USING btree (created_at);


--
-- Name: idx_daily_reports_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_reports_date ON public.daily_reports USING btree (date_rapport);


--
-- Name: idx_daily_reports_departement; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_reports_departement ON public.daily_reports USING btree (departement_id);


--
-- Name: idx_daily_reports_gps_photo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_reports_gps_photo ON public.daily_reports USING gist (gps_photo);


--
-- Name: idx_daily_reports_unite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_reports_unite ON public.daily_reports USING btree (unite_communale_id);


--
-- Name: idx_difficultes_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_difficultes_report ON public.daily_reports_difficultes USING btree (daily_report_id);


--
-- Name: idx_difficultes_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_difficultes_type ON public.daily_reports_difficultes USING btree (difficulte_id);


--
-- Name: idx_interventions_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interventions_report ON public.interventions_ponctuelles USING btree (daily_report_id);


--
-- Name: idx_mobilier_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mobilier_report ON public.mobilier_urbain USING btree (daily_report_id);


--
-- Name: idx_mobilier_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mobilier_type ON public.mobilier_urbain USING btree (type_mobilier_id);


--
-- Name: idx_personnel_apm_categorie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_apm_categorie ON public.personnel_apres_midi USING btree (categorie_id);


--
-- Name: idx_personnel_apm_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_apm_report ON public.personnel_apres_midi USING btree (daily_report_id);


--
-- Name: idx_personnel_matin_categorie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_matin_categorie ON public.personnel_matin USING btree (categorie_id);


--
-- Name: idx_personnel_matin_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_matin_report ON public.personnel_matin USING btree (daily_report_id);


--
-- Name: idx_personnel_nuit_categorie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_nuit_categorie ON public.personnel_nuit USING btree (categorie_id);


--
-- Name: idx_personnel_nuit_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_personnel_nuit_report ON public.personnel_nuit USING btree (daily_report_id);


--
-- Name: idx_photos_interventions_gps; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_photos_interventions_gps ON public.photos_interventions USING gist (gps_int);


--
-- Name: idx_photos_interventions_intervention; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_photos_interventions_intervention ON public.photos_interventions USING btree (intervention_id);


--
-- Name: idx_recommandations_report; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recommandations_report ON public.daily_reports_recommandations USING btree (daily_report_id);


--
-- Name: idx_recommandations_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recommandations_type ON public.daily_reports_recommandations USING btree (recommandation_id);


--
-- Name: idx_raw_circuits_data_gin; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_circuits_data_gin ON raw_kobo.circuits USING gin (circuit_data);


--
-- Name: idx_raw_circuits_submission; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_circuits_submission ON raw_kobo.circuits USING btree (submission_id);


--
-- Name: idx_raw_import_errors_submission; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_import_errors_submission ON raw_kobo.import_errors USING btree (submission_id);


--
-- Name: idx_raw_import_errors_type; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_import_errors_type ON raw_kobo.import_errors USING btree (error_type);


--
-- Name: idx_raw_interventions_submission; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_interventions_submission ON raw_kobo.interventions_ponctuelles USING btree (submission_id);


--
-- Name: idx_raw_mobilier_submission; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_mobilier_submission ON raw_kobo.mobilier_urbain USING btree (submission_id);


--
-- Name: idx_raw_personnel_apm_submission; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_personnel_apm_submission ON raw_kobo.personnel_apres_midi USING btree (submission_id);


--
-- Name: idx_raw_photos_intervention; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_photos_intervention ON raw_kobo.photos_interventions USING btree (intervention_id);


--
-- Name: idx_raw_submissions_date; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_submissions_date ON raw_kobo.submissions USING btree (submission_date);


--
-- Name: idx_raw_submissions_form_data_gin; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_submissions_form_data_gin ON raw_kobo.submissions USING gin (form_data);


--
-- Name: idx_raw_submissions_imported; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_submissions_imported ON raw_kobo.submissions USING btree (imported_to_mart);


--
-- Name: idx_raw_submissions_kobo_id; Type: INDEX; Schema: raw_kobo; Owner: postgres
--

CREATE INDEX idx_raw_submissions_kobo_id ON raw_kobo.submissions USING btree (kobo_submission_id);


--
-- Name: v_daily_reports_summary _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.v_daily_reports_summary AS
 SELECT dr.id,
    dr.uuid,
    dr.date_rapport,
    d.nom AS departement_nom,
    d.code AS departement_code,
    uc.nom AS unite_communale_nom,
    uc.code AS unite_communale_code,
    dr.responsable_uc,
    dr.circuits_planifies,
    dr.circuits_collectes,
    dr.tonnage_total,
    dr.depots_recurrents,
    dr.depots_recurrents_leves,
    dr.depots_sauvages,
    dr.depots_sauvages_traites,
    dr.sites_caisse,
    dr.nb_caisses,
    dr.caisses_levees,
    dr.poids_caisses,
    dr.nombre_circuits_planifies,
    dr.circuits_balayage,
    dr.km_planifies,
    dr.km_balayes,
    dr.km_desensable,
    count(DISTINCT pm.id) AS nombre_categories_personnel_matin,
    count(DISTINCT pam.id) AS nombre_categories_personnel_apm,
    count(DISTINCT pn.id) AS nombre_categories_personnel_nuit,
    count(DISTINCT cc.id) AS nombre_circuits,
    count(DISTINCT mu.id) AS nombre_types_mobilier,
    count(DISTINCT ip.id) AS nombre_interventions,
    COALESCE(sum(cc.poids_circuit), (0)::numeric) AS poids_total_circuits,
    string_agg(DISTINCT (diff.libelle)::text, ', '::text) AS difficultes_libelles,
    dr.autres_difficultes,
    string_agg(DISTINCT (rec.libelle)::text, ', '::text) AS recommandations_libelles,
    dr.autres_recommandations,
    dr.created_at,
    dr.updated_at
   FROM ((((((((((((public.daily_reports dr
     LEFT JOIN public.departements d ON ((dr.departement_id = d.id)))
     LEFT JOIN public.unites_communales uc ON ((dr.unite_communale_id = uc.id)))
     LEFT JOIN public.personnel_matin pm ON ((dr.id = pm.daily_report_id)))
     LEFT JOIN public.personnel_apres_midi pam ON ((dr.id = pam.daily_report_id)))
     LEFT JOIN public.personnel_nuit pn ON ((dr.id = pn.daily_report_id)))
     LEFT JOIN public.collection_circuits cc ON ((dr.id = cc.daily_report_id)))
     LEFT JOIN public.mobilier_urbain mu ON ((dr.id = mu.daily_report_id)))
     LEFT JOIN public.interventions_ponctuelles ip ON ((dr.id = ip.daily_report_id)))
     LEFT JOIN public.daily_reports_difficultes drd ON ((dr.id = drd.daily_report_id)))
     LEFT JOIN public.difficultes diff ON ((drd.difficulte_id = diff.id)))
     LEFT JOIN public.daily_reports_recommandations drr ON ((dr.id = drr.daily_report_id)))
     LEFT JOIN public.recommandations rec ON ((drr.recommandation_id = rec.id)))
  GROUP BY dr.id, d.nom, d.code, uc.nom, uc.code, diff.libelle, rec.libelle;


--
-- Name: collection_circuits update_collection_circuits_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_collection_circuits_updated_at BEFORE UPDATE ON public.collection_circuits FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: concessionnaires update_concessionnaires_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_concessionnaires_updated_at BEFORE UPDATE ON public.concessionnaires FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: daily_reports update_daily_reports_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_daily_reports_updated_at BEFORE UPDATE ON public.daily_reports FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: departements update_departements_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_departements_updated_at BEFORE UPDATE ON public.departements FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: interventions_ponctuelles update_interventions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON public.interventions_ponctuelles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: mobilier_urbain update_mobilier_urbain_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_mobilier_urbain_updated_at BEFORE UPDATE ON public.mobilier_urbain FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: personnel_apres_midi update_personnel_apm_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_personnel_apm_updated_at BEFORE UPDATE ON public.personnel_apres_midi FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: personnel_matin update_personnel_matin_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_personnel_matin_updated_at BEFORE UPDATE ON public.personnel_matin FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: personnel_nuit update_personnel_nuit_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_personnel_nuit_updated_at BEFORE UPDATE ON public.personnel_nuit FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: photos_interventions update_photos_interventions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_photos_interventions_updated_at BEFORE UPDATE ON public.photos_interventions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: unites_communales update_unites_communales_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_unites_communales_updated_at BEFORE UPDATE ON public.unites_communales FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: submissions update_raw_submissions_updated_at; Type: TRIGGER; Schema: raw_kobo; Owner: postgres
--

CREATE TRIGGER update_raw_submissions_updated_at BEFORE UPDATE ON raw_kobo.submissions FOR EACH ROW EXECUTE FUNCTION raw_kobo.update_updated_at_column();


--
-- Name: collection_circuits collection_circuits_concessionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_circuits
    ADD CONSTRAINT collection_circuits_concessionnaire_id_fkey FOREIGN KEY (concessionnaire_id) REFERENCES public.concessionnaires(id) ON DELETE SET NULL;


--
-- Name: collection_circuits collection_circuits_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_circuits
    ADD CONSTRAINT collection_circuits_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: collection_circuits collection_circuits_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_circuits
    ADD CONSTRAINT collection_circuits_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.circuit_status(id) ON DELETE SET NULL;


--
-- Name: daily_reports daily_reports_departement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_departement_id_fkey FOREIGN KEY (departement_id) REFERENCES public.departements(id) ON DELETE RESTRICT;


--
-- Name: daily_reports_difficultes daily_reports_difficultes_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_difficultes
    ADD CONSTRAINT daily_reports_difficultes_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: daily_reports_difficultes daily_reports_difficultes_difficulte_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_difficultes
    ADD CONSTRAINT daily_reports_difficultes_difficulte_id_fkey FOREIGN KEY (difficulte_id) REFERENCES public.difficultes(id) ON DELETE CASCADE;


--
-- Name: daily_reports daily_reports_raw_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_raw_submission_id_fkey FOREIGN KEY (raw_submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE SET NULL;


--
-- Name: daily_reports_recommandations daily_reports_recommandations_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_recommandations
    ADD CONSTRAINT daily_reports_recommandations_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: daily_reports_recommandations daily_reports_recommandations_recommandation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports_recommandations
    ADD CONSTRAINT daily_reports_recommandations_recommandation_id_fkey FOREIGN KEY (recommandation_id) REFERENCES public.recommandations(id) ON DELETE CASCADE;


--
-- Name: daily_reports daily_reports_unite_communale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_reports
    ADD CONSTRAINT daily_reports_unite_communale_id_fkey FOREIGN KEY (unite_communale_id) REFERENCES public.unites_communales(id) ON DELETE RESTRICT;


--
-- Name: interventions_ponctuelles interventions_ponctuelles_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions_ponctuelles
    ADD CONSTRAINT interventions_ponctuelles_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: mobilier_urbain mobilier_urbain_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: mobilier_urbain mobilier_urbain_observation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_observation_id_fkey FOREIGN KEY (observation_id) REFERENCES public.observations_mobilier(id) ON DELETE SET NULL;


--
-- Name: mobilier_urbain mobilier_urbain_type_mobilier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_type_mobilier_id_fkey FOREIGN KEY (type_mobilier_id) REFERENCES public.types_mobilier(id) ON DELETE SET NULL;


--
-- Name: personnel_apres_midi personnel_apres_midi_categorie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_apres_midi
    ADD CONSTRAINT personnel_apres_midi_categorie_id_fkey FOREIGN KEY (categorie_id) REFERENCES public.categories_personnel(id) ON DELETE SET NULL;


--
-- Name: personnel_apres_midi personnel_apres_midi_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_apres_midi
    ADD CONSTRAINT personnel_apres_midi_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: personnel_matin personnel_matin_categorie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_matin
    ADD CONSTRAINT personnel_matin_categorie_id_fkey FOREIGN KEY (categorie_id) REFERENCES public.categories_personnel(id) ON DELETE SET NULL;


--
-- Name: personnel_matin personnel_matin_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_matin
    ADD CONSTRAINT personnel_matin_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: personnel_nuit personnel_nuit_categorie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_nuit
    ADD CONSTRAINT personnel_nuit_categorie_id_fkey FOREIGN KEY (categorie_id) REFERENCES public.categories_personnel(id) ON DELETE SET NULL;


--
-- Name: personnel_nuit personnel_nuit_daily_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personnel_nuit
    ADD CONSTRAINT personnel_nuit_daily_report_id_fkey FOREIGN KEY (daily_report_id) REFERENCES public.daily_reports(id) ON DELETE CASCADE;


--
-- Name: photos_interventions photos_interventions_intervention_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos_interventions
    ADD CONSTRAINT photos_interventions_intervention_id_fkey FOREIGN KEY (intervention_id) REFERENCES public.interventions_ponctuelles(id) ON DELETE CASCADE;


--
-- Name: unites_communales unites_communales_departement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.unites_communales
    ADD CONSTRAINT unites_communales_departement_id_fkey FOREIGN KEY (departement_id) REFERENCES public.departements(id) ON DELETE RESTRICT;


--
-- Name: circuits circuits_submission_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.circuits
    ADD CONSTRAINT circuits_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE;


--
-- Name: import_errors import_errors_submission_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.import_errors
    ADD CONSTRAINT import_errors_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE SET NULL;


--
-- Name: interventions_ponctuelles interventions_ponctuelles_submission_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.interventions_ponctuelles
    ADD CONSTRAINT interventions_ponctuelles_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE;


--
-- Name: mobilier_urbain mobilier_urbain_submission_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.mobilier_urbain
    ADD CONSTRAINT mobilier_urbain_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE;


--
-- Name: personnel_apres_midi personnel_apres_midi_submission_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.personnel_apres_midi
    ADD CONSTRAINT personnel_apres_midi_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE;


--
-- Name: photos_interventions photos_interventions_intervention_id_fkey; Type: FK CONSTRAINT; Schema: raw_kobo; Owner: postgres
--

ALTER TABLE ONLY raw_kobo.photos_interventions
    ADD CONSTRAINT photos_interventions_intervention_id_fkey FOREIGN KEY (intervention_id) REFERENCES raw_kobo.interventions_ponctuelles(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

