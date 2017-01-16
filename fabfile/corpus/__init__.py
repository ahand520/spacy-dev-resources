from os.path import join, dirname

from fabric.api import lcd, local
from fabric.decorators import task
from fabtools.python import virtualenv

import wikipedia

SCRIPTS_DIR = "./scripts"
BROWN_DIR = SCRIPTS_DIR + "/" + "brown"
CORPUS_DIR = "./data/corpora/{lang}"
MODEL_DIR = "./data/model/{lang}"

CORPUS_VENV = ".corpus_venv"


@task
def env(env_dir=CORPUS_VENV):
    local("virtualenv {}".format(env_dir))
    with virtualenv(env_dir, local=True):
        local("pip install textacy==0.3.2 plac==0.9.6 spacy==1.6 gensim>=0.13.4 tqdm")


@task
def build_brown(path=BROWN_DIR):
    local("mkdir -p {}".format(path))
    local("git clone git@github.com:percyliang/brown-cluster.git ./{}".format(path))
    with lcd(path):
        local("make")


@task
def make_wiki_hu():
    make_wiki(CORPUS_VENV, "hu")


@task
def make_wiki(env, language):
    corpus_dir = CORPUS_DIR.format(lang=language)
    out_file = "{}_wiki.xml.bz2".format(language)
    dump_path = join(corpus_dir, out_file)
    wiki_corpus_path = join(corpus_dir, "{}_wiki.corpus".format(language))
    wiki_pages_dir = join(corpus_dir, "wiki")
    model_dir = MODEL_DIR.format(lang=language)
    word2vec_model_path = join(model_dir, "{}_wiki.word2vec".format(language))
    brown_out_dir = join(model_dir, "brown")

    wikipedia.download(corpus_dir, out_file, language)
    wikipedia.extract(env, dump_path, wiki_pages_dir, wiki_corpus_path, language)
    word2vec(wiki_corpus_path, word2vec_model_path)
    brown_clusters(wiki_corpus_path, brown_out_dir)


@task
def word2vec(corpus_path, out_path, dim=300, threads=4):
    local("mkdir -p {}".format(dirname(out_path)))
    local(
        "python -m gensim.scripts.word2vec_standalone -train {corpus_file} -output {file} -size {dim} -threads {threads}".format(
            corpus_file=corpus_path,
            dim=dim,
            file=out_path,
            threads=threads
        )
    )


@task
def brown_clusters(corpus_path, output_dir, clusters=1000, threads=4):
    local("mkdir -p {}".format(output_dir))
    brown_script = join(BROWN_DIR, "wcluster")
    local(
        "{bs} --text ./{corpus_file} --c {clusters} --output_dir {output_dir} --threads {threads}".format(
            bs=brown_script,
            corpus_file=corpus_path,
            clusters=clusters,
            threads=threads,
            output_dir=output_dir
        )
    )
