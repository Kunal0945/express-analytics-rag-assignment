from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader
)


def load_documents():

    pdf_loader = DirectoryLoader(
        "data/docs",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    text_loader = DirectoryLoader(
    "data/docs",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)

    markdown_loader = DirectoryLoader(
        "data/docs",
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    html_loader = DirectoryLoader(
        "data/docs",
        glob="**/*.html",
        loader_cls=UnstructuredHTMLLoader
    )

    pdf_docs = pdf_loader.load()
    text_docs = text_loader.load()
    markdown_docs = markdown_loader.load()
    html_docs = html_loader.load()

    documents = (
        pdf_docs +
        text_docs +
        markdown_docs +
        html_docs
    )

    return documents