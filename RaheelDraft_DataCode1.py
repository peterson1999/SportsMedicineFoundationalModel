import os
import pydicom
import numpy as np
import pandas as pd
from transformers import pipeline
import openai
import json ##احتياط إذا بتستخدمينه بعدين##

## أول خطوة: تحميل + معالجة الملفات من DICOM إلى tensors

"""
##تعمل هذه الوظيفة على معالجة ملفات DICOM بشكل متكرر وتحويلها إلى tensors متجاهلة حالة امتداد .dcm. ولا تحفظ الملف وتحتفظ به فقط في ذاكرة وقت التشغيل
    
def dicomFilesProcess(dicomFolderPath):
    
    #اختبار اضافي#
    #print(f"Processing DICOM files in folder: {dicomFolderPath}")#
    
    tensorsArr = []
    dicomFiles = []
    
    for root, _, files in os.walk(dicomFolderPath):

        #اختبار اضافي#
       #print(f"Checking folder: {root}")#

        for file in files:
            if file.lower().endswith('.dcm'):
                filePath = os.path.join(root, file)
                dicomFiles.append(filePath)
                try:
                    ds = pydicom.dcmread(filePath)
                    ## تحويل بيانات البكسل إلى tensor
                    tensor2 = np.array(ds.pixel_array)
                    tensorsArr.append(tensor2)
                except Exception as e:
                    print(f"Error reading file {filePath}: {e}")
    
    print(f"Processed {len(tensorsArr)} DICOM files.")
    return tensorsArr, dicomFiles
"""
#اختبار اضافي#
#dicomFolderPath = "PATH"  # Replace this with the actual path#
#tensorsArr, dicomFiles = dicomFilesProcess(dicomFolderPath)#

#print(f"Number of tensors: {len(tensorsArr)}")#
#print(f"First DICOM file processed: {dicomFiles[0] if dicomFiles else 'No files found'}")#
"""

"""
def dicomFilesProcessSave(dicomFolderPath, outputFolderPath):
    
    ##تعمل هذه الوظيفة على معالجة ملفات DICOM بشكل متكرر في متجهات، متجاهلة حالة امتداد .dcm، وتحفظ المتجهات كملفات .npy.
    
    if not os.path.exists(dicomFolderPath):
        ##إنشاء ملف المخرجات إذا لم يكن موجودًا
        os.makedirs(outputFolderPath) 
    
    tensorsArr = []
    dicomFiles = []
    tensorFilePaths = []
    
    for root, _, files in os.walk(dicomFolderPath):
        for file in files:
            ##تجاهل حالة الحرف
            if file.lower().endswith('.dcm'):  
                filePath = os.path.join(root, file)
                dicomFiles.append(filePath)
                try:
                    ds = pydicom.dcmread(filePath)
                    ##تحويل بيانات البكسل إلى tensor
                    tensor2 = np.array(ds.pixel_array) 
                    tensorsArr.append(tensor2)
                    
                    ##حفظ tensor على الجهاز
                    tensorFileName = os.path.splitext(file)[0] + ".npy"
                    tensorFilePath = os.path.join(outputFolderPath, tensorFileName)
                    np.save(tensorFilePath, tensor2)
                    tensorFilePaths.append(tensorFilePath)
                except Exception as e:
                    print(f"Error reading file {filePath}: {e}")
    
    print(f"Processed and saved {len(tensorsArr)} DICOM tensors.")
    return tensorFilePaths, dicomFiles

"""
#اختبار اضافي#
#dicomFolder = "/Users/raheel/Desktop/DataTestFolder"  # Replace with the path to your DICOM folder#
#tensorOutputFolder = "/Users/raheel/Desktop/DataTestFolder/Tensors"#
#tensorFilePaths, dicomFiles = dicomFilesProcessSave(dicomFolder, tensorOutputFolder)#
#print(f"Number of tensors: {len(tensorFilePaths)}")#
#print(f"First DICOM file processed: {dicomFiles[0] if dicomFiles else 'No files found'}")#
"""

##ثاني خطوة: ترجمة الأوصاف والتقارير الشعاعية من الصينية إلى الإنجليزية
def translateReport(excelPath, gptApiKey):
    
    ##ChatGPT API ترجمة التقارير بإستخدام
    
    ##ممكن تغير العامل بالرقم المفتاحي 
    openai.api_key = gptApiKey  # Replace with your OpenAI key
    df = pd.read_excel(excelPath)
    
    ##تغير الأسم حسب الجدول
    if "COLUMN1NAME" not in df.columns or "COLUMN2NAME" not in df.columns:
        raise ValueError("Expected columns 'COLUMN1NAME' and 'COLUMN2NAME' in the Excel file.")
    
    df['translatedDescription'] = df['COLUMN1NAME'].apply(
        lambda text: translateOpenAI(text) if isinstance(text, str) else ""
    )
    df['translatedReport'] = df['COLUMN2NAME'].apply(
        lambda text: translateOpenAI(text) if isinstance(text, str) else ""
    )
    
    translatedFile = os.path.join(os.path.dirname(excelPath), 'translatedData.xlsx')
    df.to_excel(translatedFile, index=False)
    print(f"Translated data saved to {translatedFile}")
    return df

def translateOpenAI(text):
    
    ##استخدام OpenAI للترجمة - ممكن استخدام الطرق الي بحثت فيها ممكن تكون أفضل من هذه الطريقة؟
    
    try:
        response = openai.ChatCompletion.create(

            ##تغير النموذج حسب المتوفر
            model="MODELNAME",

            ##تغير الرسالة إلى رسالة فيها تفاصيل أكثر
            messages=[
                {"role": "system", "content": "Translate the following text from Chinese to English:"},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return ""


## الخطوة الثالثة: دمج ملفات الDICOM مع التقارير 

def connectData(dicomFiles, csvPath, translatedDataPath):
    
    ##دمج ملفات DICOM مع التقارير بإستخدام الtarget ID
    
    csvData = pd.read_csv(csvPath)
    translatedData = pd.read_excel(translatedDataPath)


    ##تغير الأسم حسب الجدول
    if "TARGETIDCOLUMNNAME" not in csvData.columns or "PATIENTIDCOLUMNNAME" not in csvData.columns:
        raise ValueError("Expected columns 'TARGETIDCOLUMNNAME' and 'PATIENTIDCOLUMNNAME' in the CSV file.")
    
    ##تغير الأسم حسب الجدول
    if "PATIENTIDCOLUMNNAME" not in translatedData.columns:
        raise ValueError("Expected column 'PATIENTIDCOLUMNNAME' in the Excel file.")

    ##دمج المعلومات حسب رقم المريض
    mergedData = pd.merge(csvData, translatedData, on="PATIENTIDCOLUMNNAME", how="inner")
    
    ##تكوين خريطة/طريق بين رقم الهدف وجذر الملف
    targetFileMap = {os.path.basename(file): target_id for file, target_id in zip(dicomFiles, csvData['TARGETIDCOLUMNNAME'])}
    

    ##تغير الأسم حسب الجدول
    mergedData['dicomFile'] = mergedData['TARGETID'].map(targetFileMap)
    
    outputFile = os.path.join(os.path.dirname(csvPath), 'connectedData.csv')
    mergedData.to_csv(outputFile, index=False)
    print(f"Connected data saved to {outputFile}")
    return mergedData


##- Main Function مسار تدفق المعلومات الأساسي 
if __name__ == "__main__":
    ##تغير حسب المطلوب
    dicomFolder = "PATH" 
    excelPath = "PATH"  
    csvPath = "PATH"  
    gptApiKey = "KEY"  
    tensorOutputFolder = "PATH"  

   
    
    #tensors, dicomFiles = dicomFilesProcess(dicom_folder)
    tensorFilePaths, dicomFiles = dicomFilesProcessSave(dicomFolder, tensorOutputFolder)
    
  
    translatedData = translateReport(excelPath, gptApiKey)
    
 
    connectedData = connectData(dicomFiles, csvPath, os.path.join(os.path.dirname(excelPath), 'translateData.xlsx'))

    print("Pipeline completed successfully.")


"""
١- جوفي إذا طرق الترجمة الثانية تنفع
٢- تأكدي من البروسس بعد التست
٣- زيادة الميتا داتا حسب المطلوب في المودل
٤- البكسل
٥- parallel processing
٦- انكربشن بالطريقة الي تعرفينها، جوفي إذا ينفع بعد التست
"""