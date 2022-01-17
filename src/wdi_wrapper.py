#!/usr/bin/python3

from wikidataintegrator import wdi_core

# Functions to make statements in the Wikidata Integrator format


def make_statement(statement_property, statement_value, references):
    statement = wdi_core.WDItemID(
        value=statement_value, prop_nr=statement_property, references=references
    )
    return statement


def make_instance_of_cell_line_statement(reference):
    # Q21014462 -> "cell line" ; P31 -> "instance of"
    statement = make_statement(
        statement_property="P31", statement_value="Q21014462", references=reference
    )
    return statement


def make_instance_of_statement(statement_value, reference):
    statement = make_statement(
        statement_property="P31", statement_value=statement_value, references=reference
    )
    return statement


def make_instance_of_contaminated_cell_line_statement(reference):
    statement = make_statement(
        statement_property="P31", statement_value="Q27971671", references=reference
    )
    return statement


def make_established_from_disease_statement(disease_id, references):
    cell_line_from_patient_with_disease_statement = make_statement(
        statement_property="5166", statement_value=disease_id, references=references
    )
    return cell_line_from_patient_with_disease_statement
