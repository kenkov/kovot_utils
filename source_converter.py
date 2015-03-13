#! /usr/bin/env python
# coding:utf-8


import pymongo as pm
from preprocessing import TwitterPreprocessing
from textfilter import JapaneseFilter
from itertools import islice
import os


class SourceConverter:
    def __init__(
        self,
        logger,
    ):
        self.preprocessing = TwitterPreprocessing()
        self.jp_filter = JapaneseFilter()
        self.logger = logger

    def write(
        self,
        target: str,
        target_dir: str,
        texts: [str],
        source: str
    ):
        text_file = os.path.join(
            target_dir,
            "{}.txt".format(target)
        )
        text_count = 0
        total = 0

        with open(text_file, "a") as textd:
            for text in texts:
                ctext = self.preprocessing.convert(text)
                total += 1
                if self.jp_filter.is_passed(ctext):
                    print(ctext, file=textd)
                    text_count += 1
                if total % 10000 == 0:
                    self.logger.debug("text extracted: {}".format(total))
            self.logger.info(
                "{}/{} texts extracted from {} in {}".format(
                    text_count, total, source, text_file
                )
            )

    def convert_mongo2file(
        self,
        target: str,
        db: str,
        coll: str,
        host: str="localhost",
        port: int=27017,
        target_dir: str="source",
        limit: int=0,
        verbose: bool=True,
    ):
        # mongo
        client = pm.MongoClient(host, port)
        colld = client[db][coll]

        self.write(
            target,
            target_dir,
            (tweet["text"] for tweet in colld.find(
                {"text": {"$exists": True}},
                timeout=False,
                limit=limit
            )),
            "{}:{}.{}".format(host, db, coll)
        )

    def convert_file2file(
        self,
        target: str,
        file_name: str,
        target_dir: str="source",
        limit: int=0,
        verbose: bool=True,
    ):
        self.write(
            target,
            target_dir,
            islice((_.strip() for _ in open(file_name)), limit) if limit else
            (_.strip() for _ in open(file_name)),
            file_name
        )


if __name__ == '__main__':
    from logging import getLogger, basicConfig, DEBUG, INFO
    import argparse

    # parse arg
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subparser_name")
    parser_mongo = subparsers.add_parser('mongo')
    parser_mongo.add_argument(
        "target",
        type=str,
        help="target name"
    )
    parser_mongo.add_argument(
        "db",
        type=str,
        help="database name"
    )
    parser_mongo.add_argument(
        "coll",
        type=str,
        help="collection name"
    )
    parser_mongo.add_argument(
        "-l", "--limit",
        type=int,
        nargs="?",
        default=0,
        help="the number of extracted documents"
    )
    parser_mongo.add_argument(
        "-t", "--target-dir",
        type=str,
        nargs="?",
        default="source",
        help="target name"
    )
    parser_mongo.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show DEBUG log"
    )
    parser_file = subparsers.add_parser('file')
    parser_file.add_argument(
        "target",
        type=str,
        help="target name"
    )
    parser_file.add_argument(
        "file_name",
        type=str,
        help="file_name"
    )
    parser_file.add_argument(
        "-l", "--limit",
        type=int,
        nargs="?",
        default=0,
        help="the number of extracted documents"
    )
    parser_file.add_argument(
        "-t", "--target-dir",
        type=str,
        nargs="?",
        default="source",
        help="target name"
    )
    parser_file.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show DEBUG log"
    )
    logger = getLogger(__name__)

    args = parser.parse_args()

    # log
    basicConfig(
        level=DEBUG if args.verbose else INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    converter = SourceConverter(logger)
    if args.subparser_name == "mongo":
        converter.convert_mongo2file(
            target=args.target,
            db=args.db,
            coll=args.coll,
            host="localhost",
            port=27017,
            target_dir=args.target_dir,
            limit=args.limit,
            verbose=args.verbose
        )
    elif args.subparser_name == "file":
        converter.convert_file2file(
            target=args.target,
            file_name=args.file_name,
            target_dir=args.target_dir,
            limit=args.limit,
            verbose=args.verbose,
        )
