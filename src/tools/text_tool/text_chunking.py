from langchain_text_splitters import RecursiveCharacterTextSplitter as Splitter
from langchain_core.documents.base import Document

import json

class TextChunking:
    @staticmethod
    def get_subtitle_chunk(sub_path:str) -> list[Document]:
        with open(sub_path, 'r') as fi:
            trans = json.load(fi)
        docs = []

        for idx, transcript in enumerate(trans):
            # create the overlap area with neighbor scripts
            # augmented_context = transcript['text']
            if idx == 0:
                augmented_context = ' '.join([transcript['text'], trans[idx+1]['text'][:len(trans[idx+1]['text'])//3]])
            elif idx == len(trans)-1:
                augmented_context = ' '.join([trans[idx-1]['text'][-len(trans[idx-1]['text'])//3:], transcript['text']])
            else:
                augmented_context = ' '.join([trans[idx-1]['text'][-len(trans[idx-1]['text'])//3:], transcript['text'], trans[idx+1]['text'][:len(trans[idx+1]['text'])//3]])

            content = f'''
DURATION:
    Start timestamp: {str(transcript['start'])}
    End timestamp: {str(transcript['end'])}
SUBTITLE: {augmented_context}
            '''
            docs.append(Document(page_content=content))

        return docs

if __name__ == '__main__':
    print('\n'.join(TextChunking.get_subtitle_chunk('./data/video/The Android Tab/The Android Tab.json')))
