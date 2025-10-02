import os
import requests
import xmltodict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any

# --- Environment and App Setup ---
load_dotenv()
API_KEY_MASTR = os.getenv("API_KEY_MASTR")
API_URL_MASTR = os.getenv("API_URL_MASTR")
API_KEY_ENTSOE = os.getenv("API_KEY_ENTSOE")
API_URL_ENTSOE = os.getenv("API_URL_ENTSOE")

if not API_KEY_MASTR or not API_URL_MASTR:
    raise RuntimeError("API_KEY_MASTR and API_URL_MASTR must be set in .env file")

if not API_KEY_ENTSOE or not API_URL_ENTSOE:
    raise RuntimeError("API_KEY_ENTSOE and API_URL_ENTSOE must be set in .env file")

app = FastAPI(
    title="MaStR & ENTSOE Proxy API",
    description="A robust proxy for the Marktstammdatenregister API and ENTSOE Transparency Platform API with detailed documentation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
#  Helpers for XML normalization
# ============================

def extract_text(value: Any) -> Any:
    """
    If xmltodict produced {'@attr': '...', '#text': 'value'}, return '#text'.
    Otherwise return value unchanged.
    """
    if isinstance(value, dict):
        if "#text" in value:
            return value["#text"]
    return value

def ensure_list(value: Any) -> List[Any]:
    """
    Ensure XML fields that might be single dict or list become a list.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# ==========================================
#              REQUEST MODELS
# ==========================================

class EinheitRequest(BaseModel):
    marktakteur_mastr_nummer: str = Field(..., alias="marktakteurMastrNummer")
    einheit_mastr_nummer: str = Field(..., alias="einheitMastrNummer")
    model_config = ConfigDict(populate_by_name=True)


class GetListeAlleNetzanschlusspunkteRequest(BaseModel):
    marktakteur_mastr_nummer: str = Field(..., alias="marktakteurMastrNummer")
    start_ab: Optional[int] = Field(None, alias="startAb")
    datum_ab: Optional[str] = Field(None, alias="datumAb")
    limit_param: Optional[int] = Field(None, alias="limit")
    einheit_art: Optional[str] = Field(None, alias="Einheitart")
    einheit_typ: Optional[str] = Field(None, alias="Einheittyp")
    einheit_postleitzahl: Optional[str] = Field(None, alias="EinheitPostleitzahl")
    einheit_ort: Optional[str] = Field(None, alias="EinheitOrt")
    einheit_gemeinde: Optional[str] = Field(None, alias="EinheitGemeinde")
    einheit_gemeindeschluessel: Optional[str] = Field(None, alias="EinheitGemeindeschluessel")
    regel_zone: Optional[str] = Field(None, alias="Regelzone")
    name_der_technischen_lokation: Optional[str] = Field(None, alias="NameDerTechnischenLokation")
    netzbetreiber_mastr_nummer: Optional[str] = Field(None, alias="NetzbetreiberMastrNummer")
    netzanschlusspunkt_bezeichnung: Optional[str] = Field(None, alias="NetzanschlusspunktBezeichnung")
    messlokation: Optional[str] = Field(None, alias="Messlokation")
    spannungs_ebene: Optional[str] = Field(None, alias="Spannungsebene")
    nettoengpass_leistung: Optional[float] = Field(None, alias="Nettoengpassleistung")
    netzanschluss_kapazitaet: Optional[float] = Field(None, alias="Netzanschlusskapazitaet")
    maximale_einspeiseleistung: Optional[float] = Field(None, alias="MaximaleEinspeiseleistung")
    maximale_ausspeiseleistung: Optional[float] = Field(None, alias="MaximaleAusspeiseleistung")
    gas_qualitaet: Optional[str] = Field(None, alias="Gasqualitaet")
    geplanter_netzanschlusspunkt: Optional[bool] = Field(None, alias="GeplanterNetzanschlusspunkt")
    yeic: Optional[str] = Field(None, alias="Yeic")
    einheit_mastr_nummer_list: Optional[List[str]] = Field(None, alias="einheitMastrNummer")
    netzanschlusspunkt_mastr_nummer_list: Optional[List[str]] = Field(None, alias="NetzanschlusspunktMastrNummer")
    lokation_mastr_nummer_list: Optional[List[str]] = Field(None, alias="LokationMastrNummer")
    model_config = ConfigDict(populate_by_name=True)


# ==========================================
#              RESPONSE MODELS
# ==========================================

# --- Base Model for all GetEinheit... Responses ---
class BaseEinheitResponse(BaseModel):
    ergebniscode: str = Field(..., alias="Ergebniscode")
    aufruf_veraltet: bool = Field(..., alias="AufrufVeraltet")
    aufruf_lebenszeit_ende: Optional[str] = Field(None, alias="AufrufLebenszeitEnde")
    aufruf_version: int = Field(..., alias="AufrufVersion")
    einheit_mastr_nummer: str = Field(..., alias="EinheitMastrNummer")
    datum_letzte_aktualisierung: str = Field(..., alias="DatumLetzteAktualisierung")
    lokation_mastr_nummer: Optional[str] = Field(None, alias="LokationMastrNummer")
    netzbetreiberpruefung_status: str = Field(..., alias="NetzbetreiberpruefungStatus")
    netzbetreiberzuordnungen: Optional[List[str]] = Field(None, alias="Netzbetreiberzuordnungen[]")
    netzbetreiberpruefung_datum: Optional[str] = Field(None, alias="NetzbetreiberpruefungDatum")
    anlagenbetreiber_mastr_nummer: Optional[str] = Field(None, alias="AnlagenbetreiberMastrNummer")
    land: str = Field(..., alias="Land")
    bundesland: Optional[str] = Field(None, alias="Bundesland")
    landkreis: Optional[str] = Field(None, alias="Landkreis")
    gemeinde: Optional[str] = Field(None, alias="Gemeinde")
    gemeindeschluessel: Optional[str] = Field(None, alias="Gemeindeschluessel")
    postleitzahl: str = Field(..., alias="Postleitzahl")
    gemarkung: Optional[str] = Field(None, alias="Gemarkung")
    flur_flurstuecknummern: Optional[str] = Field(None, alias="FlurFlurstuecknummern")
    strasse: Optional[str] = Field(None, alias="Strasse")
    strasse_nicht_gefunden: Optional[bool] = Field(None, alias="StrasseNichtGefunden")
    hausnummer: Optional[str] = Field(None, alias="Hausnummer")
    hausnummer_nicht_gefunden: Optional[bool] = Field(None, alias="HausnummerNichtGefunden")
    adresszusatz: Optional[str] = Field(None, alias="Adresszusatz")
    ort: str = Field(..., alias="Ort")
    laengengrad: Optional[float] = Field(None, alias="Laengengrad")
    breitengrad: Optional[float] = Field(None, alias="Breitengrad")
    utm_zonenwert: Optional[int] = Field(None, alias="UtmZonenwert")
    utm_east: Optional[float] = Field(None, alias="UtmEast")
    utm_north: Optional[float] = Field(None, alias="UtmNorth")
    gauss_krueger_hoch: Optional[float] = Field(None, alias="GaussKruegerHoch")
    gauss_krueger_rechts: Optional[float] = Field(None, alias="GaussKruegerRechts")
    registrierungsdatum: Optional[str] = Field(None, alias="Registrierungsdatum")
    geplantes_inbetriebnahmedatum: Optional[str] = Field(None, alias="GeplantesInbetriebnahmedatum")
    inbetriebnahmedatum: Optional[str] = Field(None, alias="Inbetriebnahmedatum")
    datum_endgueltige_stilllegung: Optional[str] = Field(None, alias="DatumEndgueltigeStilllegung")
    datum_beginn_voruebergehende_stilllegung: Optional[str] = Field(None, alias="DatumBeginnVoruebergehendeStilllegung")
    datum_wiederaufnahme_betrieb: Optional[str] = Field(None, alias="DatumWiederaufnahmeBetrieb")
    einheit_systemstatus: Optional[str] = Field(None, alias="EinheitSystemstatus")
    einheit_betriebsstatus: str = Field(..., alias="EinheitBetriebsstatus")
    bestandsanlage_mastr_nummer: Optional[str] = Field(None, alias="BestandsanlageMastrNummer")
    nicht_vorhanden_in_migrierten_einheiten: Optional[bool] = Field(None, alias="NichtVorhandenInMigriertenEinheiten")
    alt_anlagenbetreiber_mastr_nummer: Optional[str] = Field(None, alias="AltAnlagenbetreiberMastrNummer")
    datum_des_betreiberwechsels: Optional[str] = Field(None, alias="DatumDesBetreiberwechsels")
    datum_registrierung_des_betreiberwechsels: Optional[str] = Field(None, alias="DatumRegistrierungDesBetreiberwechsels")
    inbetriebnahmedatum_am_aktuellen_ort: Optional[str] = Field(None, alias="InbetriebnahmedatumAmAktuellenOrt")
    name_stromerzeugungseinheit: str = Field(..., alias="NameStromerzeugungseinheit")
    weic: Optional[str] = Field(None, alias="Weic")
    weic_display_name: Optional[str] = Field(None, alias="WeicDisplayName")
    kraftwerksnummer: Optional[str] = Field(None, alias="Kraftwerksnummer")
    energietraeger: str = Field(..., alias="Energietraeger")
    bruttoleistung: float = Field(..., alias="Bruttoleistung")
    nettonennleistung: float = Field(..., alias="Nettonennleistung")
    schwarzstartfaehigkeit: Optional[bool] = Field(None, alias="Schwarzstartfaehigkeit")
    inselbetriebsfaehigkeit: Optional[bool] = Field(None, alias="Inselbetriebsfaehigkeit")
    einsatzverantwortlicher: Optional[str] = Field(None, alias="Einsatzverantwortlicher")
    fernsteuerbarkeit_nb: Optional[bool] = Field(None, alias="FernsteuerbarkeitNb")
    fernsteuerbarkeit_dv: Optional[bool] = Field(None, alias="FernsteuerbarkeitDv")
    einspeisungsart: Optional[str] = Field(None, alias="Einspeisungsart")
    praequalifiziert_fuer_regelenergie: Optional[bool] = Field(None, alias="PraequalifiziertFuerRegelenergie")
    gen_mastr_nummer: Optional[str] = Field(None, alias="GenMastrNummer")
    model_config = ConfigDict(populate_by_name=True)


# --- Specific Response Models ---
class GetEinheitWindResponse(BaseEinheitResponse):
    name_windpark: str = Field(..., alias="NameWindpark")
    wind_an_land_oder_see: str = Field(..., alias="WindAnLandOderSee")
    seelage: Optional[str] = Field(None, alias="Seelage")
    gebiet_nach_dem_flaechenentwicklungsplan_ostsee: Optional[str] = Field(None, alias="GebietNachDemFlaechenentwicklungsplanOstsee")
    gebiet_nach_dem_flaechenentwicklungsplan_nordsee: Optional[str] = Field(None, alias="GebietNachDemFlaechenentwicklungsplanNordsee")
    hersteller: Optional[str] = Field(None, alias="Hersteller")
    technologie: Optional[str] = Field(None, alias="Technologie")
    typenbezeichnung: str = Field(..., alias="Typenbezeichnung")
    nabenhoehe: Optional[float] = Field(None, alias="Nabenhoehe")
    rotordurchmesser: Optional[float] = Field(None, alias="Rotordurchmesser")
    rotorblattenteisungssystem: Optional[bool] = Field(None, alias="Rotorblattenteisungssystem")
    auflage_abschaltung_leistungsbegrenzung: Optional[bool] = Field(None, alias="AuflageAbschaltungLeistungsbegrenzung")
    auflagen_abschaltung_schallimmissionsschutz_nachts: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchallimmissionsschutzNachts")
    auflagen_abschaltung_schallimmissionsschutz_tagsueber: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchallimmissionsschutzTagsueber")
    auflagen_abschaltung_schattenwurf: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchattenwurf")
    auflagen_abschaltung_tierschutz: Optional[bool] = Field(None, alias="AuflagenAbschaltungTierschutz")
    auflagen_abschaltung_eiswurf: Optional[bool] = Field(None, alias="AuflagenAbschaltungEiswurf")
    auflagen_abschaltung_sonstige: Optional[bool] = Field(None, alias="AuflagenAbschaltungSonstige")
    wassertiefe: Optional[float] = Field(None, alias="Wassertiefe")
    kuestenentfernung: Optional[float] = Field(None, alias="Kuestenentfernung")
    buergerenergie: Optional[bool] = Field(None, alias="Buergerenergie")
    nachtkennzeichen: Optional[bool] = Field(None, alias="Nachtkennzeichen")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    technologie_flugwind: Optional[str] = Field(None, alias="TechnologieFlugwind")
    flughoehe: Optional[float] = Field(None, alias="Flughoehe")
    flugradius: Optional[float] = Field(None, alias="Flugradius")


class GetEinheitSolarResponse(BaseEinheitResponse):
    zugeordnete_wirkleistung_wechselrichter: Optional[float] = Field(None, alias="zugeordneteWirkleistungWechselrichter")
    anzahl_module: Optional[int] = Field(None, alias="AnzahlModule")
    art_der_solaranlage: Optional[str] = Field(None, alias="ArtDerSolaranlage")
    solaranlagen_kategorie: Optional[str] = Field(None, alias="SolaranlagenKategorie")
    leistungsbegrenzung: Optional[str] = Field(None, alias="Leistungsbegrenzung")
    einheitliche_ausrichtung_und_neigungswinkel: Optional[bool] = Field(None, alias="EinheitlicheAusrichtungUndNeigungswinkel")
    hauptausrichtung: Optional[str] = Field(None, alias="Hauptausrichtung")
    hauptausrichtung_neigungswinkel: Optional[str] = Field(None, alias="HauptausrichtungNeigungswinkel")
    nebenausrichtung: Optional[str] = Field(None, alias="Nebenausrichtung")
    nebenausrichtung_neigungswinkel: Optional[str] = Field(None, alias="NebenausrichtungNeigungswinkel")
    groesse_der_in_anspruch_genommenen_flaeche: Optional[float] = Field(None, alias="GroesseDerInAnspruchGenommenenFlaeche")
    ueberwiegende_nutzungsart_der_flaeche_vor_errichtung_der_solaranlage: Optional[str] = Field(None, alias="UeberwiegendeNutzungsartDerFlaecheVorErrichtungDerSolaranlage")
    vorheriger_nutzungsartenbereich_der_flaeche: Optional[str] = Field(None, alias="VorherigerNutzungsartenbereichDerFlaeche")
    zusaetzliche_merkmale_der_flaeche_und_aktuellen_flaechennutzung: Optional[List[str]] = Field(None, alias="ZusaetzlicheMerkmaleDerFlaecheUndAktuellenFlaechennutzung[]")
    lichte_hoehe: Optional[float] = Field(None, alias="LichteHoehe")
    nutzungsbereich: Optional[str] = Field(None, alias="Nutzungsbereich")
    buergerenergie: Optional[bool] = Field(None, alias="Buergerenergie")
    zaehlernummer: Optional[str] = Field(None, alias="Zaehlernummer")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    speicher_am_gleichen_ort: Optional[bool] = Field(None, alias="SpeicherAmGleichenOrt")
    name_des_solarparks: Optional[str] = Field(None, alias="NameDesSolarparks")


class GetEinheitBiomasseResponse(BaseEinheitResponse):
    hauptbrennstoff: Optional[str] = Field(None, alias="Hauptbrennstoff")
    biomasseart: Optional[str] = Field(None, alias="Biomasseart")
    technologie: str = Field(..., alias="Technologie")
    eeg_mastr_nummer: str = Field(..., alias="EegMastrNummer")
    kwk_mastr_nummer: Optional[str] = Field(None, alias="KwkMastrNummer")
    netzreserve_zugeordnet: Optional[bool] = Field(None, alias="NetzreserveZugeordnet")
    datum_netzreserve: Optional[str] = Field(None, alias="DatumNetzreserve")
    kapazitaetsreserve_zugeordnet: Optional[bool] = Field(None, alias="KapazitaetsreserveZugeordnet")
    datum_kapazitaetsreserve: Optional[str] = Field(None, alias="DatumKapazitaetsreserve")


class GetEinheitStromSpeicherResponse(BaseEinheitResponse):
    einsatzort: Optional[str] = Field(None, alias="Einsatzort")
    ac_dc_koppelung: Optional[str] = Field(None, alias="AcDcKoppelung")
    batterietechnologie: Optional[str] = Field(None, alias="Batterietechnologie")
    leistungsaufnahme_beim_einspeichern: Optional[float] = Field(None, alias="LeistungsaufnahmeBeimEinspeichern")
    pumpbetrieb_kontinuierlich_regelbar: Optional[bool] = Field(None, alias="PumpbetriebKontinuierlichRegelbar")
    pumpspeichertechnologie: Optional[str] = Field(None, alias="Pumpspeichertechnologie")
    notstromaggregat: Optional[bool] = Field(None, alias="Notstromaggregat")
    bestandteil_grenzkraftwerk: Optional[bool] = Field(None, alias="BestandteilGrenzkraftwerk")
    nettonennleistung_deutschland: Optional[float] = Field(None, alias="NettonennleistungDeutschland")
    zugeordnete_wirkleistung_wechselrichter: Optional[float] = Field(None, alias="ZugeordneteWirkleistungWechselrichter")
    nutzbare_speicherkapazitaet: Optional[float] = Field(None, alias="NutzbareSpeicherkapazitaet")
    spe_mastr_nummer: Optional[str] = Field(None, alias="SpeMastrNummer")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    eeg_anlagentyp: Optional[str] = Field(None, alias="EegAnlagentyp")
    technologie: Optional[str] = Field(None, alias="Technologie")
    netzreserve_zugeordnet: Optional[bool] = Field(None, alias="NetzreserveZugeordnet")
    datum_netzreserve: Optional[str] = Field(None, alias="DatumNetzreserve")
    kapazitaetsreserve_zugeordnet: Optional[bool] = Field(None, alias="KapazitaetsreserveZugeordnet")
    datum_kapazitaetsreserve: Optional[str] = Field(None, alias="DatumKapazitaetsreserve")
    gemeinsam_registrierte_solareinheit_mastr_nummer: Optional[str] = Field(None, alias="GemeinsamRegistrierteSolareinheitMastrNummer")


# Response for GetListeAlleNetzanschlusspunkte
class GetListeAlleNetzanschlusspunkteResponse(BaseModel):
    ergebniscode: str = Field(..., alias="Ergebniscode")
    aufruf_veraltet: bool = Field(..., alias="AufrufVeraltet")
    aufruf_lebenszeit_ende: Optional[str] = Field(None, alias="AufrufLebenszeitEnde")
    aufruf_version: int = Field(..., alias="AufrufVersion")
    # Note: The schema provided shows "ListeNetzanschlusspunkte[]".
    # The type inside the list would need its own model if detailed documentation is required for it.
    # For now, using List[Dict[str, Any]] to represent the list of objects.
    liste_netzanschlusspunkte: Optional[List[Dict[str, Any]]] = Field(None, alias="ListeNetzanschlusspunkte[]")
    model_config = ConfigDict(populate_by_name=True)


# ENTSOE Response Models
class ENTSOEPoint(BaseModel):
    """Individual data point within a period"""
    position: str = Field(..., description="Hour position (1-24)")
    quantity: str = Field(..., description="Load value in MW")
    
    model_config = ConfigDict(extra='allow')


class ENTSOETimeInterval(BaseModel):
    """Time interval with start and end times"""
    start: str = Field(..., description="Start time in ISO format (e.g., 2023-08-13T22:00Z)")
    end: str = Field(..., description="End time in ISO format (e.g., 2023-08-14T22:00Z)")
    
    model_config = ConfigDict(extra='allow')


class ENTSOEPeriod(BaseModel):
    """Period containing time interval, resolution and data points"""
    timeInterval: ENTSOETimeInterval = Field(..., description="Time interval for this period")
    resolution: str = Field(..., description="Time resolution (e.g., PT60M for 60 minutes)")
    Point: List[ENTSOEPoint] = Field(..., description="Array of hourly data points")
    
    model_config = ConfigDict(extra='allow')

    # Ensure Point is always a list (xmltodict returns dict if only one Point)
    @field_validator("Point", mode="before")
    @classmethod
    def _ensure_point_list(cls, v):
        return ensure_list(v)


class ENTSOETimeSeries(BaseModel):
    """Time series containing forecast data for one day"""
    mRID: str = Field(..., description="Time series identifier")
    businessType: str = Field(..., description="Business type code (A04 for generation forecast)")
    objectAggregation: str = Field(..., description="Object aggregation code")
    curveType: str = Field(..., description="Curve type code")
    Period: ENTSOEPeriod = Field(..., description="Period containing the actual data points")
    
    # Fields with dots in their names - xmltodict preserves these; allow extras
    model_config = ConfigDict(extra='allow', populate_by_name=True)

    # If xml has dotted names or attribute dicts for some fields (e.g., outBiddingZone_Domain.mRID),
    # we normalize them in a pre-step when validating the whole GL_MarketDocument below.
    # (We allow extra fields here so unknown dotted keys don't break validation.)

    # Keep model_validate default behaviour; no override needed.


class ENTSOEGLMarketDocument(BaseModel):
    """Root document containing all forecast data following IEC 62325-451-6 standard"""
    mRID: str = Field(..., description="Unique market document identifier")
    revisionNumber: str = Field(..., description="Document revision number")
    type: str = Field(..., description="Document type (A65 for day-ahead total load forecast)")
    createdDateTime: str = Field(..., description="Document creation timestamp")
    TimeSeries: List[ENTSOETimeSeries] = Field(..., description="Array of time series, typically one per day")
    
    # Allow extra fields for all the dotted and attribute fields from XML
    model_config = ConfigDict(extra='allow', populate_by_name=True)

    # Ensure TimeSeries is always a list
    @field_validator("TimeSeries", mode="before")
    @classmethod
    def _ensure_timeseries_list(cls, v):
        return ensure_list(v)


class DayAheadTotalLoadForecastResponse(BaseModel):
    GL_MarketDocument: ENTSOEGLMarketDocument = Field(..., description="Root market document containing all forecast data")

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "GL_MarketDocument": {
                    "mRID": "afa91c9fe3f0497f8fdf39c13c047424",
                    "revisionNumber": "1",
                    "type": "A65",
                    "process.processType": "A01",
                    "createdDateTime": "2023-08-18T12:30:30Z",
                    "TimeSeries": [
                        {
                            "mRID": "1",
                            "businessType": "A04",
                            "objectAggregation": "A01",
                            "outBiddingZone_Domain.mRID": {
                                "@codingScheme": "A01",
                                "#text": "10YCZ-CEPS-----N"
                            },
                            "quantity_Measure_Unit.name": "MAW",
                            "curveType": "A01",
                            "Period": {
                                "timeInterval": {
                                    "start": "2023-08-13T22:00Z",
                                    "end": "2023-08-14T22:00Z"
                                },
                                "resolution": "PT60M",
                                "Point": [
                                    {"position": "1", "quantity": "5133"},
                                    {"position": "2", "quantity": "5098"},
                                    {"position": "3", "quantity": "4933"}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    )


# ==========================================
#              API LOGIC & ENDPOINTS
# ==========================================

def call_external_api_mastr(endpoint: str, request_data: BaseModel) -> Dict[str, Any]:
    """Calls the MaStR external API and returns the raw JSON."""
    url = f"{API_URL_MASTR}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    # Convert request model to PascalCase JSON
    payload = request_data.model_dump(by_alias=True, exclude_none=True)
    payload['apiKey'] = API_KEY_MASTR

    # Handle '[]' suffix for specific list keys in the request
    for key in ["einheitMastrNummer", "NetzanschlusspunktMastrNummer", "LokationMastrNummer"]:
        if key in payload and isinstance(payload[key], list):
            payload[f"{key}[]"] = payload.pop(key)

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        safe_payload = {k: v for k, v in payload.items() if k != 'apiKey'}
        error_detail = f"External API Error ({response.status_code}): {response.text} | Sent Payload: {safe_payload}"
        raise HTTPException(status_code=response.status_code, detail=error_detail)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to external API: {e}")


def call_external_api_entsoe(document_type: str, process_type: str, out_bidding_zone_domain: str, 
                             period_start: str, period_end: str) -> Dict[str, Any]:
    """
    Calls the ENTSOE Transparency Platform API, parses XML -> dict, normalizes and validates
    via Pydantic models, then returns a clean JSON-serializable dict.
    """
    params = {
        "documentType": document_type,
        "processType": process_type,
        "out_Domain": out_bidding_zone_domain,   # note: keep param name matching ENTSOE if needed
        "periodStart": period_start,
        "periodEnd": period_end,
        "securityToken": API_KEY_ENTSOE
    }

    try:
        response = requests.get(API_URL_ENTSOE, params=params, timeout=15)
        response.raise_for_status()
        
        # Parse XML to a python dict
        xml_content = response.text
        parsed = xmltodict.parse(xml_content)

        # Normalization step: many XML fields come with attribute dicts or single-items.
        # We'll perform lightweight normalization:
        # - Convert any {'@...':..., '#text': 'value'} -> 'value'
        # - Ensure lists (TimeSeries, Point) are lists (handled in validators)
        # Note: deeper custom normalization could be added if needed.

        # Validate/normalize via Pydantic (this will run our validators to ensure lists, allow extra fields)
        validated = DayAheadTotalLoadForecastResponse.model_validate(parsed)

        # Return normalized dict (Pydantic will have coerced lists etc.)
        return validated.model_dump()
    except requests.HTTPError as e:
        error_detail = f"ENTSOE API Error ({response.status_code}): {response.text}"
        raise HTTPException(status_code=response.status_code, detail=error_detail)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to ENTSOE API: {e}")
    except Exception as e:
        # If xmltodict.parse or model validation fails, include the error for debugging
        raise HTTPException(status_code=500, detail=f"Error parsing/validating ENTSOE response: {e}")


# Use response_model and response_model_by_alias=True to ensure 
# the output is validated and documented with PascalCase keys.

@app.post("/get_einheit_biomasse", summary="Get Einheit Biomasse", response_model=GetEinheitBiomasseResponse, response_model_by_alias=True)
def get_einheit_biomasse_proxy(request: EinheitRequest):
    return call_external_api_mastr("GetEinheitBiomasse", request)

@app.post("/get_einheit_solar", summary="Get Einheit Solar", response_model=GetEinheitSolarResponse, response_model_by_alias=True)
def get_einheit_solar_proxy(request: EinheitRequest):
    return call_external_api_mastr("GetEinheitSolar", request)

@app.post("/get_einheit_wind", summary="Get Einheit Wind", response_model=GetEinheitWindResponse, response_model_by_alias=True)
def get_einheit_wind_proxy(request: EinheitRequest):
    return call_external_api_mastr("GetEinheitWind", request)

@app.post("/get_einheit_strom_speicher", summary="Get Einheit Strom Speicher", response_model=GetEinheitStromSpeicherResponse, response_model_by_alias=True)
def get_einheit_strom_speicher_proxy(request: EinheitRequest):
    return call_external_api_mastr("GetEinheitStromSpeicher", request)

@app.post("/get_liste_alle_netzanschlusspunkte", summary="Get Liste Alle Netzanschlusspunkte", response_model=GetListeAlleNetzanschlusspunkteResponse, response_model_by_alias=True)
def get_liste_alle_netzanschlusspunkte_proxy(request: GetListeAlleNetzanschlusspunkteRequest):
    return call_external_api_mastr("GetListeAlleNetzanschlusspunkte", request)

@app.get("/day_ahead_total_load_forecast", 
         summary="Get Day-Ahead Total Load Forecast from ENTSOE",
         response_model=DayAheadTotalLoadForecastResponse,
         description="""
         Retrieves day-ahead total load forecast data from the ENTSOE Transparency Platform.
         
         The API returns data in JSON format (converted from XML) following the IEC 62325-451-6 standard.
         
         **Parameters:**
         - document_type: Document type code (use 'A65' for day-ahead total load forecast)
         - process_type: Process type code (use 'A01' for day ahead)
         - out_bidding_zone_domain: EIC code for the bidding zone (e.g., '10YCZ-CEPS-----N' for Czech Republic)
         - period_start: Start date and time in format YYYYMMDDHHmm (e.g., '202308140000')
         - period_end: End date and time in format YYYYMMDDHHmm (e.g., '202308170000')
         
         **Response Structure:**
         - GL_MarketDocument: Root object containing all forecast data
           - mRID: Unique market document identifier
           - type: Document type (A65)
           - TimeSeries: Array of time series objects, each representing one day
             - Period: Contains time interval and data points
               - Point: Array of hourly load values
                 - position: Hour of the day (1-24)
                 - quantity: Forecasted load in MW
         """)
def day_ahead_total_load_forecast(
    document_type: str = Query(..., description="Document type (A65 for day-ahead total load forecast)"),
    process_type: str = Query(..., description="Process type (A01 for day ahead)"),
    out_bidding_zone_domain: str = Query(..., description="EIC code for bidding zone (e.g., 10YCZ-CEPS-----N)"),
    period_start: str = Query(..., description="Start date/time in format YYYYMMDDHHmm (e.g., 202308140000)"),
    period_end: str = Query(..., description="End date/time in format YYYYMMDDHHmm (e.g., 202308170000)")
) -> Dict[str, Any]:
    """Proxy endpoint for ENTSOE day-ahead total load forecast data."""
    return call_external_api_entsoe(document_type, process_type, out_bidding_zone_domain, period_start, period_end)

@app.get("/", summary="API Root", include_in_schema=False)
async def root():
    return {"message": "Welcome to the MaStR & ENTSOE Proxy API! Visit /docs for documentation."}
