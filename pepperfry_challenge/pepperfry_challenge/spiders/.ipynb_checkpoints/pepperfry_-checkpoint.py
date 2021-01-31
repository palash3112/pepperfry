import scrapy
import requests
import json
import os

class pepperfry(scrapy.Spider):
    name = "pepperfry"
    BASE_DIR='./pepperfry/'
    Max_Cnt=0  

    def start_requests(self):
        BASE_url ="https://www.pepperfry.com/site_product/search?q="
                  
       
        items=['arm chairs','two seater sofa','bean bags','bench','book case','chest drawers','coffee tables','dining set',
              'king beds','queens bed','garden seating']
        urls_l=[]
        dir_names=[]
        for item in items:
            url_string="+".join(item.split(' '))
            dir_name="-".join(item.split(' '))
            dir_names.append(dir_name)
            urls_l.append(BASE_url+url_string)
            dir_path=self.BASE_DIR+dir_name
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
        for i in range(len(urls_l)):
            d={
                "dir_name":dir_names[i]            
            }
            resp=scrapy.Request(url=urls_l[i],callback=self.parser,dont_filter=True)
            print(resp)
            resp.meta['dir_name']=dir_names[i]
            yield resp
            
    def parser(self,response,**meta):
        product_urls=response.xpath('//div/div/div/a[@p=0]/@href').extract()
        counter=0
        for url in product_urls:
            resp=scrapy.Request(url=url,callback=self.parser,dont_filter=True)
            resp.meta['dir_name']=response.meta['dir_name']
            if counter==self.Max_Cnt:
                break
            if not resp==None:
                counter+=1
            yield resp
    def parse_item(self,response,**metadata):
        item_title=response.xpath('//div/div/div/h1/text()').extracty()[0]
        item_price=response.xpath('//div/div/div/p/b[@class="pf-orange-color pf-large font-20 pf-primary-color"]/text()').extract()[0].strip()
        item_saving=response.xpath('//p[@class="pf-margin-0 pf-bold-txt font-13"]/text()').extract[0].strip()
        item_description=response.xpath('//div[@itemprop="description"]/div/p/text()').extract()
        item_details_key=response.xpath('//div[@id="itemDetail"]/p/b/text()').extract()
        item_detail_values=response.xpath('//div[@id="itemDetail"]/p/text()').extract()
        a=len(item_details_key)
        b=len(item_detail_values)
        idetail={}
        for i in range(min(a,b)):
            idetail[item_details_key[i]]=item_detail_values[i]
        stop_items=["Pepperfry!.com","we also offer you a","so go ahead and buy with you confidence."]
        item_description=filter(lambda x: all([not y.lower() in x.lower() for y in stop_items]),item_description)
        item_description='\n'.join(item_description)
        img_url_l=response.xpath('//li[@class="vip-options-slideeach"]/a/@data-img').extract()
        if (len(img_url_l)>3):
            d={
                "item Name": item_title,
                "description":item_description,
                "Item Price":item_price,
                "Savings":item_saving,
                "Details":idetail
            }
            CATEGORY_NAME=response.meta('dir_name')
            ITEM_DIR_URL=os.path.join(self.BASE_DIR,os.path.join(CATEGORY_NAME,item_title))
            if not os.path.exists(ITEM_DIR_URL):
                os.makedirs(ITEM_DIR_URL)
            with open(os.path.join(ITEM_DIR_URL,'metadata.txt'),'w') as f:
                json.dump(d,f)
            for i,img_url in enumerate(img_url_l):
                r=request.get(img_url)
                with open(os.path.join(ITEM_DIR_URL,"image{}.jpg".format(i),"wb")) as f:
                          f.write(r.content)  
            print("successfull")
            yield d
        yield None
    
            