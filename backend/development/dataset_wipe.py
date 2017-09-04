from ckanapi import RemoteCKAN

my_ckan = RemoteCKAN('https://demo.ckan.org', apikey='051a57ad-5636-4aa6-b685-262b7ab96401')

package = my_ckan.action.package_show(id ='produtores-rn')

for resource in package.get('resources'):
    my_ckan.action.resource_delete(id=resource.get('id'))